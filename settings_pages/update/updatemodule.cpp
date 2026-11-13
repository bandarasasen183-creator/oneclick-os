#include "updatemodule.h"

#include <KPluginFactory>
#include <QDir>
#include <QFile>
#include <QRegularExpression>

K_PLUGIN_CLASS_WITH_JSON(UpdateModule, "kcm_oneclick_update.json")

static const QString HELPER = QStringLiteral("/usr/libexec/oneclick-update-helper");

UpdateModule::UpdateModule(QObject *parent, const KPluginMetaData &data)
    : KQuickConfigModule(parent, data)
{
    setButtons(NoAdditionalButton);
    m_currentVersion = readFileTrimmed(QStringLiteral("/usr/share/oneclick/version"));
    const QString saved = readFileTrimmed(QStringLiteral("/var/lib/oneclick/channel"));
    if (saved == QLatin1String("security")) {
        m_channel = saved;
    }
    m_progressTimer.setInterval(1000);
    connect(&m_progressTimer, &QTimer::timeout, this, &UpdateModule::sampleProgress);
}

QString UpdateModule::readFileTrimmed(const QString &path)
{
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) {
        return {};
    }
    return QString::fromUtf8(f.readAll()).trimmed();
}

// Total bytes received on all real network interfaces. The download is by far the biggest
// traffic while updating, so the change in this number is a fair measure of progress.
qint64 UpdateModule::receivedBytes()
{
    qint64 total = 0;
    const QDir net(QStringLiteral("/sys/class/net"));
    for (const QString &name : net.entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
        if (name == QLatin1String("lo")) {
            continue;
        }
        total += readFileTrimmed(net.filePath(name + QStringLiteral("/statistics/rx_bytes"))).toLongLong();
    }
    return total;
}

void UpdateModule::setState(const QString &state, const QString &message)
{
    m_state = state;
    m_message = message;
    Q_EMIT stateChanged();
}

void UpdateModule::runHelper(const QStringList &args, bool isDownload, bool restartAfter)
{
    if (m_process) {
        return; // one thing at a time
    }
    m_isDownload = isDownload;
    m_restartAfter = restartAfter;
    m_lastOutput.clear();
    if (isDownload) {
        m_totalMb = 0;
        m_doneMb = 0;
        m_eta.clear();
        m_startBytes = receivedBytes();
        m_clock.start();
        m_progressTimer.start();
        Q_EMIT progressChanged();
    }

    m_process = new QProcess(this);
    m_process->setProcessChannelMode(QProcess::MergedChannels);
    connect(m_process, &QProcess::readyReadStandardOutput, this, [this]() {
        const QString text = QString::fromUtf8(m_process->readAllStandardOutput());
        for (const QString &line : text.split(QRegularExpression(QStringLiteral("[\r\n]+")), Qt::SkipEmptyParts)) {
            onHelperLine(line.trimmed());
        }
    });
    connect(m_process, &QProcess::finished, this, [this, args](int code, QProcess::ExitStatus) {
        m_progressTimer.stop();
        m_process->deleteLater();
        m_process = nullptr;
        const QString command = args.value(0);

        if (code == 126 || code == 127) { // password prompt cancelled
            setState(QStringLiteral("idle"));
            return;
        }
        if (code != 0) {
            setState(QStringLiteral("error"), m_lastOutput);
            return;
        }
        if (command == QLatin1String("check")) {
            if (m_lastOutput == QLatin1String("STAGED")) {
                setState(QStringLiteral("ready"));
            } else if (m_lastOutput == QLatin1String("AVAILABLE")) {
                setState(QStringLiteral("available"));
            } else {
                setState(QStringLiteral("uptodate"));
            }
            return;
        }
        // download, switch or rollback finished
        m_doneMb = m_totalMb;
        m_eta.clear();
        Q_EMIT progressChanged();
        if (m_restartAfter) {
            restart();
        } else {
            setState(QStringLiteral("ready"));
        }
    });
    m_process->start(QStringLiteral("pkexec"), QStringList{HELPER} + args);
}

void UpdateModule::onHelperLine(const QString &line)
{
    if (line.isEmpty()) {
        return;
    }
    m_lastOutput = line;
    // e.g. "layers already present: 258; layers needed: 1 (303.0 MB)"
    static const QRegularExpression needed(QStringLiteral("layers needed: \\d+ \\(([0-9.]+)\\s*([kMG])i?B\\)"));
    const auto match = needed.match(line);
    if (match.hasMatch()) {
        double value = match.captured(1).toDouble();
        const QString unit = match.captured(2);
        if (unit == QLatin1String("G")) {
            value *= 1024;
        } else if (unit == QLatin1String("k")) {
            value /= 1024;
        }
        m_totalMb = value;
        m_startBytes = receivedBytes();
        m_clock.restart();
        Q_EMIT progressChanged();
    }
}

void UpdateModule::sampleProgress()
{
    if (m_totalMb <= 0) {
        return;
    }
    const double done = qMin(m_totalMb, (receivedBytes() - m_startBytes) / 1048576.0);
    m_doneMb = qMax(m_doneMb, done);
    const double seconds = m_clock.elapsed() / 1000.0;
    if (seconds > 3 && m_doneMb > 1 && m_doneMb < m_totalMb) {
        const int left = int((m_totalMb - m_doneMb) / (m_doneMb / seconds));
        if (left < 60) {
            m_eta = QStringLiteral("less than a minute left");
        } else if (left < 3600) {
            m_eta = QStringLiteral("about %1 min left").arg((left + 30) / 60);
        } else {
            m_eta = QStringLiteral("about %1 h %2 min left").arg(left / 3600).arg((left % 3600) / 60);
        }
    } else if (m_doneMb >= m_totalMb) {
        m_eta = QStringLiteral("finishing up...");
    }
    Q_EMIT progressChanged();
}

void UpdateModule::check()
{
    setState(QStringLiteral("checking"));
    runHelper({QStringLiteral("check"), m_channel}, false, false);
}

void UpdateModule::download(bool restartAfter)
{
    setState(QStringLiteral("downloading"));
    runHelper({QStringLiteral("download"), m_channel}, true, restartAfter);
}

void UpdateModule::setChannel(const QString &channel)
{
    if (channel == m_channel || (channel != QLatin1String("full") && channel != QLatin1String("security"))) {
        return;
    }
    m_channel = channel;
    Q_EMIT channelChanged();
    setState(QStringLiteral("idle"));
}

void UpdateModule::installVersion(const QString &version, bool restartAfter)
{
    setState(QStringLiteral("downloading"));
    runHelper({QStringLiteral("version"), version}, true, restartAfter);
}

void UpdateModule::rollback()
{
    setState(QStringLiteral("downloading"));
    runHelper({QStringLiteral("rollback")}, false, false);
}

void UpdateModule::restart()
{
    QProcess::startDetached(QStringLiteral("systemctl"), {QStringLiteral("reboot")});
}

void UpdateModule::loadVersions()
{
    auto *list = new QProcess(this);
    connect(list, &QProcess::finished, this, [this, list](int code, QProcess::ExitStatus) {
        if (code == 0) {
            m_versions = QString::fromUtf8(list->readAllStandardOutput()).split(QLatin1Char('\n'), Qt::SkipEmptyParts);
            Q_EMIT versionsChanged();
        }
        list->deleteLater();
    });
    list->start(HELPER, {QStringLiteral("versions")}); // no password needed to list
}

#include "updatemodule.moc"
