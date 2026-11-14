// OneClick website back end. Lives in the Codecraft Firebase project as its own codebase
// ("oneclick"), so deploying it never touches the Codecraft site's functions.
//
// oneclickReport: takes a problem report from oneclickos.org/report and files it as an issue
// in github.com/Codecraft-Solutions-Team/oneclick-os. No account needed to report.
// The reporter's email, if given, is never put in the public issue: it is stored privately in
// Firestore next to the issue number, so we can reply.
const { onRequest } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const admin = require("firebase-admin");

admin.initializeApp();
const GITHUB_TOKEN = defineSecret("ONECLICK_GITHUB_TOKEN");
const REPO = "Codecraft-Solutions-Team/oneclick-os";
const KINDS = {
  "Something doesn't work": "bug",
  "It won't install or start": "install",
  "A game or app won't run": "compatibility",
  "It looks wrong": "design",
  "An idea or request": "idea",
  "A problem with this website": "website",
};
const clip = (v, n) => String(v || "").replace(/\r/g, "").trim().slice(0, n);

// Simple per-address limit: at most 5 reports per 10 minutes.
const recent = new Map();
function tooMany(ip) {
  const now = Date.now(), list = (recent.get(ip) || []).filter(t => now - t < 600000);
  list.push(now); recent.set(ip, list);
  return list.length > 5;
}

exports.oneclickReport = onRequest(
  { secrets: [GITHUB_TOKEN], region: "us-central1", memory: "256MiB", maxInstances: 3 },
  async (req, res) => {
    if (req.method !== "POST") return res.status(405).json({ error: "Use POST" });
    const b = req.body || {};
    if (b.website) return res.json({ ok: true });                    // hidden field only bots fill in
    const ip = String(req.headers["x-forwarded-for"] || req.ip || "").split(",")[0].trim();
    if (tooMany(ip)) return res.status(429).json({ error: "Too many reports from here. Please try again in a few minutes." });

    const kind = KINDS[b.kind] ? b.kind : "Something doesn't work";
    const what = clip(b.what, 4000);
    if (what.length < 10) return res.status(400).json({ error: "Please describe what happened in a few words." });
    const expected = clip(b.expected, 2000), pc = clip(b.pc, 200), version = clip(b.version, 40), email = clip(b.email, 200);

    const title = `[${KINDS[kind]}] ${what.split("\n")[0].slice(0, 80)}`;
    const body = [
      `**Type:** ${kind}`,
      "", "**What happened**", what,
      expected && "\n**What they expected**\n" + expected,
      "", `**Computer:** ${pc || "not given"}`, `**OneClick version:** ${version || "not given"}`,
      "", "_Sent from the report form on the OneClick website._",
    ].filter(x => x !== false && x !== "").join("\n");

    const r = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
      method: "POST",
      headers: { Authorization: `Bearer ${GITHUB_TOKEN.value()}`, Accept: "application/vnd.github+json", "User-Agent": "oneclick-report-form" },
      body: JSON.stringify({ title, body, labels: ["tester report", KINDS[kind]] }),
    });
    if (!r.ok) {
      console.error("GitHub said", r.status, await r.text());
      return res.status(502).json({ error: "We couldn't file your report just now. Please try again soon." });
    }
    const issue = await r.json();
    if (email) {
      await admin.firestore().collection("oneclick_report_contacts").doc(String(issue.number))
        .set({ email, issue: issue.number, created: admin.firestore.FieldValue.serverTimestamp() });
    }
    res.json({ ok: true, number: issue.number, url: issue.html_url });
  }
);
