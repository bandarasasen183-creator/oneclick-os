/* ---------- look: "story" (storybook) or "classic". Open any page with ?style=classic or ?style=story to switch. ---------- */
(function () {
  let style = 'story';
  try { const q = new URLSearchParams(location.search).get('style'); if (q) localStorage.setItem('oneclick-style', q); style = localStorage.getItem('oneclick-style') || style; } catch (e) {}
  document.documentElement.dataset.style = style === 'classic' ? 'classic' : 'story';
})();

/* ---------- colour mode: follows the device until the person chooses ---------- */
(function () {
  let saved = null; try { saved = localStorage.getItem('oneclick-theme'); } catch (e) {}
  const apply = t => { document.documentElement.dataset.theme = t;
    document.querySelectorAll('img[data-wordmark]').forEach(i => i.src = 'assets/wordmark-' + (t === 'light' ? 'light' : 'dark') + '.svg'); };
  const current = () => saved || (document.documentElement.dataset.style === 'story' || matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  apply(current());
  document.addEventListener('DOMContentLoaded', () => {
    apply(current());
    const b = document.getElementById('theme');
    if (b) b.onclick = () => { saved = current() === 'light' ? 'dark' : 'light'; try { localStorage.setItem('oneclick-theme', saved); } catch (e) {} apply(saved); };
  });
})();

/* ---------- writes the OneClick wordmark by hand, then drops the dot onto the i ---------- */
window.OneClickWrite = function (svg, onDone) {
  const strokes = [...svg.querySelectorAll('path[data-w]')];
  const odot = svg.querySelector('.o'), idot = svg.querySelector('.i');
  const WRITE = 1.75;
  const total = strokes.reduce((a, s) => a + +s.dataset.w, 0);
  let acc = 0;
  const timing = strokes.map(s => { const a = acc / total * WRITE; acc += +s.dataset.w; return [a, acc / total * WRITE]; });
  strokes.forEach(s => { const L = s.getTotalLength(); s.style.strokeDasharray = L; s.style.strokeDashoffset = L; s.dataset.len = L; });
  const ease = p => p * p * (3 - 2 * p);
  // the i-dot fades in out of the dark above the i, drops, squashes on landing, bounces twice
  const G = 2600, REST = 72, START = -40, BOUNCE = 0.42, T0 = WRITE + 0.12;
  const samples = (() => { const out = []; let y = START, v = 0, hits = 0;
    for (let t = 0; t < 1.6; t += 1 / 240) { v += G / 240; y += v / 240; let sq = 0;
      if (y >= REST && v > 0) { y = REST; hits++; sq = Math.min(0.32, v / 2600); v = hits < 3 ? -v * BOUNCE : 0; }
      out.push([y, sq]); } return out; })();
  function dot(t) {
    t -= T0; if (t < 0) return null;
    const i = Math.min(Math.floor(t * 240), samples.length - 1);
    let sq = 0; for (let k = Math.max(0, i - 19); k <= i; k++) sq = Math.max(sq, samples[k][1]);
    return [samples[i][0], sq, Math.min(1, t / 0.14)];
  }
  function draw(t) {
    strokes.forEach((s, i) => { const [a, b] = timing[i]; const p = t <= a ? 0 : ease(Math.min(1, (t - a) / (b - a))); s.style.strokeDashoffset = s.dataset.len * (1 - p); });
    const q = Math.max(0, Math.min(1, (t - timing[0][1]) / 0.16));
    odot.setAttribute('r', 17 * q * (1.3 - 0.3 * q));
    const d = dot(t);
    if (d) { const g = 0.6 + 0.4 * d[2], rx = 15 * (1 + d[1]) * g, ry = 15 * (1 - d[1]) * g;
      idot.setAttribute('rx', rx); idot.setAttribute('ry', ry); idot.setAttribute('cy', d[0] + 15 - ry); idot.setAttribute('opacity', d[2]); }
  }
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { draw(99); onDone && onDone(); return; }
  let start = null; const end = T0 + 1.3;
  requestAnimationFrame(function frame(now) {
    if (start === null) start = now;
    const t = (now - start) / 1000 - 0.35;
    draw(Math.max(0, t));
    if (t < end) requestAnimationFrame(frame); else onDone && onDone();
  });
};
(function () { const hero = document.querySelector('svg.word'); if (hero) window.OneClickWrite(hero); })();

/* ---------- reveal on scroll ---------- */
(function () {
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .15 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
})();

/* ---------- app picker ---------- */
(function () {
  // locked: part of the system, always included. on: ticked by default. mb: rough download size.
  const A = (n, d, c, col, extra = {}) => ({ n, d, c, col, mb: 120, ...extra });
  const APPS = [
    A('Files', 'Browse and organise your files', ['system'], '#e8a317', { locked: true }),
    A('Settings', 'Everything about your PC in one place', ['system'], '#5b6b86', { locked: true }),
    A('App Store', 'Install and update thousands of apps', ['system'], '#3b82f6', { locked: true }),
    A('Update', 'New versions, security fixes and going back', ['system'], '#0d9488', { locked: true }),
    A('Text Editor', 'Notes and plain text', ['system', 'office'], '#64748b', { locked: true }),
    A('Screenshot', 'Capture the screen or a window', ['system'], '#e11d48', { locked: true }),
    A('Task Manager', 'See what is running and end it', ['system'], '#0f766e', { locked: true }),
    A('Firefox', 'Fast, private web browser', ['internet', 'popular'], '#e66000', { on: true, mb: 90 }),
    A('Google Chrome', 'Web browser by Google', ['internet', 'popular'], '#1a73e8', { mb: 110 }),
    A('Brave', 'Browser with built-in ad blocking', ['internet'], '#fb542b', { mb: 110 }),
    A('Microsoft Edge', 'Microsoft’s browser, synced with your account', ['internet'], '#0c7cd5', { mb: 150 }),
    A('Thunderbird', 'Email and calendar', ['internet', 'office'], '#0a84ff', { mb: 100 }),
    A('Zoom', 'Video meetings', ['internet', 'office'], '#2d8cff', { mb: 140 }),
    A('Microsoft Teams (web)', 'Teams in its own window', ['internet', 'office'], '#5b5fc7', { mb: 1 }),
    A('WhatsApp (web)', 'Chats from your phone on your PC', ['internet', 'popular'], '#25d366', { mb: 1 }),
    A('Telegram', 'Messaging with sync across devices', ['internet'], '#2aabee', { mb: 60 }),
    A('Signal', 'Private messaging', ['internet'], '#3a76f0', { mb: 150 }),
    A('Claude', 'AI assistant by Anthropic', ['ai', 'popular'], '#d97757', { on: true, mb: 1 }),
    A('ChatGPT', 'AI assistant by OpenAI', ['ai', 'popular'], '#10a37f', { on: true, mb: 1 }),
    A('Gemini', 'AI assistant by Google', ['ai'], '#4285f4', { mb: 1 }),
    A('Copilot', 'AI assistant by Microsoft', ['ai'], '#0f6cbd', { mb: 1 }),
    A('Perplexity', 'AI search with sources', ['ai'], '#20808d', { mb: 1 }),
    A('LibreOffice', 'Writer, Calc and Impress. Opens Word, Excel and PowerPoint files', ['office', 'popular'], '#18a303', { on: true, mb: 350 }),
    A('OnlyOffice', 'Office suite with a Microsoft Office layout', ['office'], '#ff6f3d', { mb: 300 }),
    A('Office on the web', 'Word, Excel and PowerPoint online', ['office'], '#d83b01', { mb: 1 }),
    A('Google Docs and Drive', 'Docs, Sheets, Slides and Drive', ['office'], '#1fa463', { mb: 1 }),
    A('OneDrive', 'Your OneDrive as a folder in Files', ['office'], '#0364b8', { mb: 20 }),
    A('PDF Reader', 'Read, sign and fill in PDFs', ['system', 'office'], '#c0392b', { locked: true, mb: 40 }),
    A('Obsidian', 'Notes linked together', ['office'], '#7c3aed', { mb: 200 }),
    A('Steam', 'Thousands of Windows games through Proton', ['gaming', 'popular'], '#1b2838', { mb: 400 }),
    A('Heroic Games Launcher', 'Epic Games, GOG and Amazon Prime games', ['gaming'], '#5c2ad1', { mb: 200 }),
    A('Lutris', 'Battle.net, EA, Ubisoft and older games', ['gaming'], '#ff9800', { mb: 80 }),
    A('Bottles', 'Run Windows programs', ['gaming', 'system'], '#c2410c', { on: true, mb: 150 }),
    A('GeForce NOW', 'Cloud gaming, including games that block Linux', ['gaming'], '#76b900', { mb: 1 }),
    A('Xbox Cloud Gaming', 'Play Game Pass games in the cloud', ['gaming'], '#107c10', { mb: 1 }),
    A('Minecraft', 'The Java Edition launcher', ['gaming', 'popular'], '#3c8527', { mb: 250 }),
    A('Discord', 'Voice and chat for games and friends', ['gaming', 'internet', 'popular'], '#5865f2', { mb: 120 }),
    A('MangoHud', 'Frame rate and temperatures over your game', ['gaming'], '#e11d48', { mb: 10 }),
    A('Controller support', 'Xbox, PlayStation and Switch pads', ['gaming'], '#475569', { mb: 15 }),
    A('Spotify', 'Music and podcasts', ['media', 'popular'], '#1db954', { mb: 200 }),
    A('VLC', 'Plays any video or audio file', ['media', 'popular'], '#ff8800', { on: true, mb: 80 }),
    A('Stremio', 'Films and series in one place', ['media'], '#7b5bf5', { mb: 150 }),
    A('Plex', 'Your own film library, anywhere', ['media'], '#e5a00d', { mb: 120 }),
    A('Photos', 'View and tidy your pictures', ['system', 'media'], '#0ea5e9', { locked: true, mb: 30 }),
    A('GIMP', 'Photo editing', ['creative'], '#5c5543', { mb: 300 }),
    A('Krita', 'Painting and drawing', ['creative'], '#2c8fd0', { mb: 250 }),
    A('Inkscape', 'Logos and vector drawings', ['creative'], '#1d1d1b', { mb: 200 }),
    A('Kdenlive', 'Video editing', ['creative', 'media'], '#527eb2', { mb: 250 }),
    A('DaVinci Resolve', 'Professional video editing and colour', ['creative'], '#2c2c2c', { mb: 3000 }),
    A('OBS Studio', 'Record and stream your screen', ['creative', 'gaming'], '#302e31', { mb: 200 }),
    A('Blender', '3D modelling and animation', ['creative'], '#e87d0d', { mb: 400 }),
    A('Audacity', 'Record and edit audio', ['creative', 'media'], '#0000cc', { mb: 80 }),
    A('Figma (web)', 'Design and prototyping', ['creative'], '#a259ff', { mb: 1 }),
    A('Visual Studio Code', 'Code editor', ['developer'], '#007acc', { mb: 350 }),
    A('Git and GitHub Desktop', 'Version control with a simple window', ['developer'], '#6e5494', { mb: 150 }),
    A('Python', 'Programming language and tools', ['developer'], '#3776ab', { mb: 100 }),
    A('Node.js', 'JavaScript runtime', ['developer'], '#3c873a', { mb: 80 }),
    A('Docker', 'Run containers', ['developer'], '#2496ed', { mb: 300 }),
    A('Bitwarden', 'Password manager', ['utilities'], '#175ddc', { mb: 120 }),
    A('Proton VPN', 'Private VPN', ['utilities', 'internet'], '#6d4aff', { mb: 100 }),
    A('Backups', 'Automatic backups to a drive or the cloud', ['system', 'utilities'], '#0891b2', { locked: true, mb: 20 }),
    A('Phone Link', 'Texts, files and notifications from your phone', ['system', 'utilities'], '#2dd4bf', { locked: true, mb: 20 }),
    A('Disk Usage', 'See what is filling your disk', ['system', 'utilities'], '#f59e0b', { locked: true, mb: 10 }),
    A('Archives', 'Open and make zip and rar files', ['system', 'utilities'], '#ca8a04', { locked: true, mb: 10 }),
  ];
  const CATS = [['all', 'All'], ['popular', 'Popular'], ['gaming', 'Gaming'], ['office', 'Office'], ['ai', 'AI'], ['internet', 'Internet'], ['media', 'Media'], ['creative', 'Creative'], ['developer', 'Developer'], ['utilities', 'Utilities'], ['system', 'Built in']];
  const PRESETS = [
    ['Everyday', 'Browser, office, media', ['Firefox', 'LibreOffice', 'VLC', 'Photos', 'WhatsApp (web)', 'Spotify', 'Claude', 'ChatGPT']],
    ['Gamer', 'Steam, launchers, Discord', ['Steam', 'Heroic Games Launcher', 'Lutris', 'Bottles', 'Discord', 'MangoHud', 'Controller support', 'GeForce NOW', 'OBS Studio']],
    ['Work', 'Office, meetings, cloud', ['LibreOffice', 'Office on the web', 'OneDrive', 'Google Docs and Drive', 'Zoom', 'Microsoft Teams (web)', 'Thunderbird', 'PDF Reader']],
    ['Creator', 'Photo, video, audio', ['GIMP', 'Krita', 'Kdenlive', 'Audacity', 'OBS Studio', 'Blender', 'Inkscape']],
  ];
  const ICONS = {"Firefox": "assets/apps/org.mozilla.firefox.png", "Google Chrome": "assets/apps/com.google.Chrome.png", "Brave": "assets/apps/com.brave.Browser.png", "Microsoft Edge": "assets/apps/com.microsoft.Edge.png", "Thunderbird": "assets/apps/org.mozilla.Thunderbird.png", "Zoom": "assets/apps/us.zoom.Zoom.png", "Telegram": "assets/apps/org.telegram.desktop.png", "Signal": "assets/apps/org.signal.Signal.png", "LibreOffice": "assets/apps/org.libreoffice.LibreOffice.png", "OnlyOffice": "assets/apps/org.onlyoffice.desktopeditors.png", "PDF Reader": "assets/apps/oneclick-reader.svg", "Obsidian": "assets/apps/md.obsidian.Obsidian.png", "Steam": "assets/apps/com.valvesoftware.Steam.png", "Heroic Games Launcher": "assets/apps/com.heroicgameslauncher.hgl.png", "Lutris": "assets/apps/net.lutris.Lutris.png", "Bottles": "assets/apps/com.usebottles.bottles.png", "Minecraft": "assets/apps/com.mojang.Minecraft.png", "Discord": "assets/apps/com.discordapp.Discord.png", "Spotify": "assets/apps/com.spotify.Client.png", "VLC": "assets/apps/org.videolan.VLC.png", "Stremio": "assets/apps/com.stremio.Stremio.png", "Plex": "assets/apps/tv.plex.PlexDesktop.png", "Photos": "assets/apps/oneclick-photos.svg", "GIMP": "assets/apps/org.gimp.GIMP.png", "Krita": "assets/apps/org.kde.krita.png", "Inkscape": "assets/apps/org.inkscape.Inkscape.png", "Kdenlive": "assets/apps/org.kde.kdenlive.png", "OBS Studio": "assets/apps/com.obsproject.Studio.png", "Blender": "assets/apps/org.blender.Blender.png", "Audacity": "assets/apps/org.audacityteam.Audacity.png", "Visual Studio Code": "assets/apps/com.visualstudio.code.png", "Git and GitHub Desktop": "assets/apps/io.github.shiftey.Desktop.png", "Bitwarden": "assets/apps/com.bitwarden.desktop.png", "Proton VPN": "assets/apps/com.protonvpn.www.png", "Disk Usage": "assets/apps/oneclick-diskusage.svg", "Archives": "assets/apps/oneclick-archive.svg", "Claude": "assets/apps/logo-claude.png", "ChatGPT": "assets/apps/logo-chatgpt.png", "Gemini": "assets/apps/logo-gemini.svg", "Copilot": "assets/apps/web-copilot-microsoft-com.png", "Perplexity": "assets/apps/logo-perplexity.png", "Microsoft Teams (web)": "assets/apps/web-teams-microsoft-com.png", "Office on the web": "assets/apps/web-office-com.png", "Google Docs and Drive": "assets/apps/logo-google.png", "OneDrive": "assets/apps/web-onedrive-live-com.png", "GeForce NOW": "assets/apps/web-nvidia-com.png", "Xbox Cloud Gaming": "assets/apps/web-xbox-com.png", "Figma (web)": "assets/apps/web-figma-com.png", "DaVinci Resolve": "assets/apps/logo-davinci.png", "Python": "assets/apps/web-python-org.png", "Node.js": "assets/apps/logo-nodejs.svg", "Docker": "assets/apps/web-docker-com.png", "WhatsApp (web)": "assets/apps/logo-whatsapp.png", "Files": "assets/apps/oneclick-files.svg", "Settings": "assets/apps/oneclick-settings.svg", "App Store": "assets/apps/oneclick-store.svg", "Update": "assets/apps/oneclick-update.svg", "Text Editor": "assets/apps/oneclick-editor.svg", "Screenshot": "assets/apps/oneclick-screenshot.svg", "Task Manager": "assets/apps/oneclick-monitor.svg", "Backups": "assets/apps/oneclick-settings-disks.svg", "Phone Link": "assets/apps/oneclick-phone.svg", "Controller support": "assets/apps/oneclick-settings-touch.svg", "MangoHud": "assets/apps/oneclick-monitor.svg"};
  const byName = Object.fromEntries(APPS.map(a => [a.n, a]));
  const chosen = new Set(APPS.filter(a => a.on || a.locked).map(a => a.n));
  let cat = 'all';
  const $ = id => document.getElementById(id);
  if (!$('list')) return;
  const list = $('list'), tabs = $('tabs'), q = $('q'), sum = $('summary'), tray = $('tray');
  const initials = n => n.replace(/\(.*?\)/g, '').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('');

  PRESETS.forEach(([title, sub, names]) => {
    const b = document.createElement('button');
    b.innerHTML = `<b>${title}</b><span>${sub}</span>`;
    b.onclick = () => { names.forEach(n => chosen.add(n)); render(); tray.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); };
    $('presets').appendChild(b);
  });
  CATS.forEach(([id, label]) => {
    const b = document.createElement('button');
    b.className = 'tab'; b.setAttribute('role', 'tab'); b.dataset.id = id;
    const count = id === 'all' ? APPS.length : APPS.filter(a => a.c.includes(id)).length;
    b.innerHTML = `${label}<span class="count">${count}</span>`;
    b.onclick = () => { cat = id; render(); };
    tabs.appendChild(b);
  });

  function toggle(a) { if (a.locked) return; chosen.has(a.n) ? chosen.delete(a.n) : chosen.add(a.n); render(); }

  function render() {
    tabs.querySelectorAll('.tab').forEach(t => t.setAttribute('aria-selected', t.dataset.id === cat));
    const term = q.value.trim().toLowerCase();
    const shown = APPS.filter(a => (term ? true : (cat === 'all' || a.c.includes(cat))) && (!term || (a.n + ' ' + a.d + ' ' + a.c.join(' ')).toLowerCase().includes(term)));
    list.innerHTML = '';
    if (!shown.length) list.innerHTML = '<div class="empty">No apps match that. Thousands more are in the App Store after you install.</div>';
    shown.forEach(a => {
      const el = document.createElement('div');
      el.className = 'app' + (chosen.has(a.n) ? ' on' : '') + (a.locked ? ' locked' : '');
      el.setAttribute('role', 'checkbox'); el.setAttribute('aria-checked', chosen.has(a.n)); el.tabIndex = a.locked ? -1 : 0;
      el.innerHTML = `${ICONS[a.n] ? `<img class="ico img" src="${ICONS[a.n]}" alt="" loading="lazy">` : `<div class="ico" style="background:${a.col}">${initials(a.n)}</div>`}<div class="txt"><b>${a.n}</b><span>${a.d}</span>${a.locked ? '<span class="tag">Part of the system</span>' : ''}</div><div class="box"></div>`;
      el.onclick = () => toggle(a);
      el.onkeydown = e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); toggle(a); } };
      list.appendChild(el);
    });
    const picked = [...chosen].map(n => byName[n]).filter(a => !a.locked);
    tray.innerHTML = picked.length ? '' : '<span class="hint">Nothing extra chosen. That’s fine: you can add apps any time.</span>';
    picked.forEach(a => {
      const c = document.createElement('span');
      c.className = 'chip';
      c.innerHTML = `${a.n}<button aria-label="Remove ${a.n}">&times;</button>`;
      c.querySelector('button').onclick = () => toggle(a);
      tray.appendChild(c);
    });
    const mb = picked.reduce((t, a) => t + a.mb, 0);
    const size = mb >= 1000 ? (mb / 1024).toFixed(1) + ' GB' : mb + ' MB';
    sum.textContent = `${picked.length} apps chosen, about ${size} extra`;
  }
  q.addEventListener('input', render);
  render();
})();

/* ---------- download page: tick the box to enable the buttons ---------- */
(function () {
  const box = document.getElementById('understand');
  if (!box) return;
  const set = () => document.querySelectorAll('.build .btn').forEach(b => b.setAttribute('aria-disabled', !box.checked));
  box.addEventListener('change', set); set();
})();

/* ---------- report form: builds an email to us with the details filled in ---------- */
(function () {
  const f = document.getElementById('report');
  if (!f) return;
  f.addEventListener('submit', e => {
    e.preventDefault();
    const d = new FormData(f), line = (k, label) => d.get(k) ? label + ': ' + d.get(k) + '\n' : '';
    const body = line('kind', 'Type') + '\n' + line('what', 'What happened') + '\n' + line('expected', 'Expected') + '\n' + line('pc', 'Computer') + line('version', 'Version') + line('email', 'Reply to');
    location.href = 'mailto:oneclick@codecraftsol.org?subject=' + encodeURIComponent('OneClick report: ' + d.get('kind')) + '&body=' + encodeURIComponent(body);
  });
})();
