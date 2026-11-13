// The Update page in Settings.
// All privileged work is done by /usr/libexec/oneclick-update-helper through pkexec;
// this class runs it, reads its output, and tracks download progress for the page.
#pragma once

#include <KQuickConfigModule>
#include <QElapsedTimer>
#include <QProcess>
#include <QStringList>
#include <QTimer>

class UpdateModule : public KQuickConfigModule
{
    Q_OBJECT
    // idle, checking, available, uptodate, downloading, ready, error
    Q_PROPERTY(QString state READ state NOTIFY stateChanged)
    Q_PROPERTY(QString message READ message NOTIFY stateChanged)
    Q_PROPERTY(QString currentVersion READ currentVersion CONSTANT)
    Q_PROPERTY(QString channel READ channel NOTIFY channelChanged)          // "full" or "security"
    Q_PROPERTY(QStringList versions READ versions NOTIFY versionsChanged)   // newest first
    Q_PROPERTY(double totalMb READ totalMb NOTIFY progressChanged)
    Q_PROPERTY(double doneMb READ doneMb NOTIFY progressChanged)
    Q_PROPERTY(QString eta READ eta NOTIFY progressChanged)

public:
    UpdateModule(QObject *parent, const KPluginMetaData &data);

    QString state() const { return m_state; }
    QString message() const { return m_message; }
    QString currentVersion() const { return m_currentVersion; }
    QString channel() const { return m_channel; }
    QStringList versions() const { return m_versions; }
    double totalMb() const { return m_totalMb; }
    double doneMb() const { return m_doneMb; }
    QString eta() const { return m_eta; }

    Q_INVOKABLE void check();
    Q_INVOKABLE void download(bool restartAfter);                 // newest for the current channel
    Q_INVOKABLE void setChannel(const QString &channel);          // "full" or "security"
    Q_INVOKABLE void installVersion(const QString &version, bool restartAfter);
    Q_INVOKABLE void rollback();
    Q_INVOKABLE void restart();
    Q_INVOKABLE void loadVersions();

Q_SIGNALS:
    void stateChanged();
    void channelChanged();
    void versionsChanged();
    void progressChanged();

private:
    void setState(const QString &state, const QString &message = QString());
    void runHelper(const QStringList &args, bool isDownload, bool restartAfter);
    void onHelperLine(const QString &line);
    void sampleProgress();
    static qint64 receivedBytes();
    static QString readFileTrimmed(const QString &path);

    QString m_state = QStringLiteral("idle");
    QString m_message;
    QString m_currentVersion;
    QString m_channel = QStringLiteral("full");
    QStringList m_versions;
    double m_totalMb = 0;
    double m_doneMb = 0;
    QString m_eta;

    QProcess *m_process = nullptr;
    QTimer m_progressTimer;
    QElapsedTimer m_clock;
    qint64 m_startBytes = 0;
    bool m_restartAfter = false;
    bool m_isDownload = false;
    QString m_lastOutput;
};
