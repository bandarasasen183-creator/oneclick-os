/* A small working model of the OneClick desktop for the home page.
   Start menu with search, draggable windows with working buttons, Files, Settings (which really
   changes the taskbar and accent colour), a text editor you can type in, and Update, which
   downloads a pretend update and restarts into the start-up animation. */
(function () {
  const root = document.getElementById('demo');
  if (!root) return;
  const A = 'assets/apps/';
  const APPS = {
    files:    { name: 'Files',       icon: A + 'oneclick-files.svg',    w: 520, h: 330 },
    settings: { name: 'Settings',    icon: A + 'oneclick-settings.svg', w: 540, h: 360 },
    update:   { name: 'Update',      icon: A + 'oneclick-update.svg',   w: 440, h: 280 },
    editor:   { name: 'Text Editor', icon: A + 'oneclick-editor.svg',   w: 440, h: 300 },
    store:    { name: 'App Store',   icon: A + 'oneclick-store.svg',    w: 500, h: 330 },
  };
  const PINNED = ['files', 'store', 'settings', 'update'];
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };

  root.innerHTML = `
    <div class="wall"><img src="assets/logo.svg" alt=""></div>
    <div class="dicons">
      <div class="dicon" data-open="files"><img src="${A}oneclick-files.svg" alt="">Home</div>
      <div class="dicon" data-open="editor"><img src="${A}oneclick-editor.svg" alt="">Notes.txt</div>
      <div class="dicon" data-open="store"><img src="${A}oneclick-store.svg" alt="">App Store</div>
    </div>
    <div class="pop" id="d-vol"><div style="display:flex;gap:10px;align-items:center"><img src="${A}tray-audio-high.svg" width="18" alt=""><input type="range" min="0" max="100" value="70" aria-label="Volume"><span id="d-volv">70%</span></div></div>
    <div class="pop" id="d-cal"></div>
    <div class="toast" id="d-toast"></div>
    <div class="menu" id="d-menu">
      <input placeholder="Search apps and settings" aria-label="Search">
      <h4>Pinned</h4><div class="tiles"></div>
      <div class="power"><button data-p="restart">Restart</button><button data-p="reset">Reset demo</button></div>
    </div>
    <div class="edge"></div>
    <div class="bar">
      <button class="tb" id="d-start" aria-label="Start"><img src="assets/logo.svg" alt=""></button>
      <span id="d-pins" style="display:flex;gap:4px"></span>
      <div class="tray">
        <img src="${A}tray-bell.svg" alt="" title="No new notifications"><img src="${A}tray-audio-high.svg" alt="" id="d-volb" title="Volume" style="cursor:pointer"><img src="${A}tray-brightness.svg" alt="" title="Brightness"><img src="${A}tray-wired.svg" alt="" title="Connected">
        <div class="clock" id="d-clock" style="cursor:pointer"><div id="d-time"></div><div id="d-date"></div></div>
      </div>
      <div class="corner" title="Show the home screen"></div>
    </div>`;
  const menu = root.querySelector('#d-menu'), pins = root.querySelector('#d-pins'), tiles = menu.querySelector('.tiles'), search = menu.querySelector('input');
  const wins = {}; let z = 10;

  // ---- clock ----
  const tick = () => { const d = new Date();
    root.querySelector('#d-time').textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    root.querySelector('#d-date').textContent = d.toLocaleDateString(); };
  tick(); setInterval(tick, 20000);

  // ---- taskbar and start menu ----
  function pinButtons() {
    pins.innerHTML = '';
    const ids = [...new Set([...PINNED, ...Object.keys(wins)])];
    ids.forEach(id => { const b = el('button', 'tb' + (wins[id] ? ' open' : ''), `<img src="${APPS[id].icon}" alt="${APPS[id].name}">`);
      b.title = APPS[id].name; b.onclick = () => wins[id] && !wins[id].hidden && wins[id].style.zIndex == z ? minimise(id) : open(id); pins.appendChild(b); });
    root.classList.toggle('home', !Object.values(wins).some(w => !w.hidden));
  }
  function fillMenu(term = '') {
    tiles.innerHTML = '';
    const extra = [['Taskbar settings', 'settings', 'taskbar'], ['Check for updates', 'update'], ['Colours', 'settings', 'look']];
    const items = Object.keys(APPS).map(id => [APPS[id].name, id]).concat(term ? extra : []);
    items.filter(i => i[0].toLowerCase().includes(term.toLowerCase())).forEach(([name, id, page]) => {
      const t = el('div', 'tile-app', `<img src="${APPS[id].icon}" alt="">${name}`);
      t.onclick = () => { toggleMenu(false); open(id, page); }; tiles.appendChild(t); });
    if (!tiles.children.length) tiles.innerHTML = '<div style="grid-column:1/-1;padding:14px;color:#8a97ae">Nothing found</div>';
    menu.querySelector('h4').textContent = term ? 'Results' : 'Pinned';
  }
  function toggleMenu(show) {
    const on = show ?? !menu.classList.contains('show');
    menu.classList.toggle('show', on);
    if (on) { search.value = ''; fillMenu(); search.focus({ preventScroll: true }); }
  }
  root.querySelector('#d-start').onclick = e => { e.stopPropagation(); toggleMenu(); };
  search.oninput = () => fillMenu(search.value.trim());
  search.onkeydown = e => { if (e.key === 'Enter' && tiles.firstElementChild?.onclick) tiles.firstElementChild.onclick(); if (e.key === 'Escape') toggleMenu(false); };
  menu.onclick = e => e.stopPropagation();
  root.addEventListener('click', () => toggleMenu(false));
  root.querySelector('.corner').onclick = () => { Object.keys(wins).forEach(id => { wins[id].hidden = true; }); pinButtons(); };
  menu.querySelectorAll('.power button').forEach(b => b.onclick = () => { toggleMenu(false); b.dataset.p === 'reset' ? reset() : boot(); });

  // ---- windows ----
  function focus(w) { w.style.zIndex = ++z; }
  function minimise(id) { const w = wins[id]; w.classList.add('mini'); setTimeout(() => { w.hidden = true; w.classList.remove('mini'); pinButtons(); }, 200); }
  function close(id) { const w = wins[id]; if (!w) return; w.classList.add('closing'); setTimeout(() => { w.remove(); delete wins[id]; pinButtons(); }, 150); }
  function open(id, page) {
    if (wins[id]) { wins[id].hidden = false; focus(wins[id]); if (page) wins[id].show?.(page); pinButtons(); return; }
    const a = APPS[id], n = Object.keys(wins).length;
    const w = el('div', 'win');
    const W = Math.min(a.w, root.clientWidth - 20), H = Math.min(a.h, root.clientHeight - 70);
    Object.assign(w.style, { width: W + 'px', height: H + 'px', left: Math.max(8, (root.clientWidth - W) / 2 + (n % 3 - 1) * 34) + 'px', top: Math.max(8, (root.clientHeight - 46 - H) / 2 + (n % 3 - 1) * 22) + 'px' });
    w.innerHTML = `<div class="title"><img src="${a.icon}" alt=""><span>${a.name}</span>
        <button class="wb" data-a="min" aria-label="Minimise"><svg viewBox="0 0 10 10"><path d="M0 5.5H10"/></svg></button>
        <button class="wb" data-a="max" aria-label="Maximise"><svg viewBox="0 0 10 10"><rect x=".5" y=".5" width="9" height="9"/></svg></button>
        <button class="wb x" data-a="close" aria-label="Close"><svg viewBox="0 0 10 10"><path d="M0 0L10 10M10 0L0 10"/></svg></button>
      </div><div class="body"></div>`;
    w.addEventListener('pointerdown', () => focus(w));
    w.querySelector('[data-a=min]').onclick = () => minimise(id);
    w.querySelector('[data-a=max]').onclick = () => w.classList.toggle('max');
    w.querySelector('[data-a=close]').onclick = () => close(id);
    const title = w.querySelector('.title');
    title.ondblclick = () => w.classList.toggle('max');
    title.addEventListener('pointerdown', e => {
      if (e.target.closest('.wb') || w.classList.contains('max')) return;
      const r = root.getBoundingClientRect(), sx = e.clientX - w.offsetLeft, sy = e.clientY - w.offsetTop;
      title.setPointerCapture(e.pointerId);
      const move = ev => { w.style.left = Math.min(r.width - 60, Math.max(60 - w.offsetWidth, ev.clientX - sx)) + 'px'; w.style.top = Math.min(r.height - 80, Math.max(0, ev.clientY - sy)) + 'px'; };
      const up = () => { title.removeEventListener('pointermove', move); title.removeEventListener('pointerup', up); };
      title.addEventListener('pointermove', move); title.addEventListener('pointerup', up);
    });
    wins[id] = w; root.appendChild(w); focus(w);
    BUILD[id](w.querySelector('.body'), w); if (page) w.show?.(page);
    pinButtons();
  }

  // ---- the apps ----
  const sw = (on, fn) => { const b = el('button', 'sw' + (on ? ' on' : '')); b.onclick = () => { b.classList.toggle('on'); fn(b.classList.contains('on')); }; return b; };
  const row = (title, sub, control) => { const r = el('div', 'row', `<div>${title}<small>${sub}</small></div>`); r.appendChild(control); return r; };
  const BUILD = {
    files(body) {
      const tree = { Home: ['Documents', 'Downloads', 'Pictures', 'Music', 'Videos'], Documents: ['Homework.odt', 'Budget.ods', 'Notes.txt'], Downloads: ['setup.exe', 'photo.jpg'], Pictures: ['Holiday', 'Screenshots'], Music: [], Videos: [] };
      body.innerHTML = '<div class="split"><div class="side"></div><div class="pane"><div class="files"></div></div></div>';
      const side = body.querySelector('.side'), files = body.querySelector('.files');
      const go = where => {
        side.innerHTML = ''; Object.keys(tree).forEach(k => { const d = el('div', k === where ? 'on' : '', `<img src="${A}oneclick-files.svg" alt="">${k}`); d.onclick = () => go(k); side.appendChild(d); });
        files.innerHTML = (tree[where] || []).length ? '' : '<div style="grid-column:1/-1;color:#8a97ae;padding:30px;text-align:center">Folder is empty</div>';
        (tree[where] || []).forEach(n => { const isFile = n.includes('.'); const f = el('div', 'file', `<img src="${A}${isFile ? 'oneclick-editor' : 'oneclick-files'}.svg" alt="">${n}`);
          f.ondblclick = () => isFile ? (n.endsWith('.exe') ? alert('"setup.exe" is a Windows program. On OneClick it opens with the built-in Windows app support.') : open('editor')) : (tree[n] ? go(n) : go('Home')); files.appendChild(f); });
      }; go('Home');
    },
    settings(body, w) {
      body.innerHTML = '<div class="split"><div class="side"></div><div class="pane"></div></div>';
      const side = body.querySelector('.side'), pane = body.querySelector('.pane');
      const pages = {
        taskbar: ['Taskbar', A + 'oneclick-settings.svg', () => {
          pane.appendChild(row('Floating', 'A rounded bar with a gap around it', sw(root.classList.contains('floating'), on => root.classList.toggle('floating', on))));
          pane.appendChild(row('Hide automatically', 'Hidden while an app is open, always shown on the home screen', sw(root.classList.contains('hide'), on => root.classList.toggle('hide', on))));
        }],
        look: ['Colours', A + 'oneclick-photos.svg', () => {
          const s = el('div', 'swatches');
          ['#2dd4bf', '#60a5fa', '#f472b6', '#fbbf24', '#a78bfa'].forEach(c => { const b = el('button'); b.style.background = c; b.onclick = () => { root.style.setProperty('--acc', c); document.querySelectorAll('#demo .tb.open').forEach(() => {}); accent(c); s.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b)); }; s.appendChild(b); });
          pane.appendChild(row('Accent colour', 'Used for highlights and switches', s));
        }],
        update: ['Update', A + 'oneclick-update.svg', () => { pane.innerHTML = '<p style="color:#8a97ae;margin-top:0">Updates have their own window in this demo.</p>'; const b = el('button', 'dbtn', 'Open Update'); b.onclick = () => open('update'); pane.appendChild(b); }],
      };
      w.show = id => { side.innerHTML = ''; Object.entries(pages).forEach(([k, p]) => { const d = el('div', k === id ? 'on' : '', `<img src="${p[1]}" alt="">${p[0]}`); d.onclick = () => w.show(k); side.appendChild(d); }); pane.innerHTML = ''; pages[id][2](); };
      w.show('taskbar');
    },
    update(body) {
      const p = el('div', 'pane'); body.appendChild(p);
      const state = s => {
        if (s === 'idle') { p.innerHTML = '<h3 style="margin:0 0 6px">A new version is available</h3><p style="color:#8a97ae;margin:0 0 16px">OneClick OS 0.2. Nothing installs unless you choose to.</p>';
          const a = el('button', 'dbtn', 'Download and restart'), b = el('button', 'dbtn alt', 'Download'); b.style.marginLeft = '8px'; a.onclick = () => run(true); b.onclick = () => run(false); p.append(a, b); }
        if (s === 'done') { p.innerHTML = '<h3 style="margin:0 0 6px">Ready. Restart to finish</h3><p style="color:#8a97ae;margin:0 0 16px">Your open apps will close when you restart.</p>';
          const a = el('button', 'dbtn', 'Restart now'); a.onclick = boot; p.appendChild(a); }
      };
      const run = restart => { const total = 303; let done = 0; p.innerHTML = '<h3 style="margin:0 0 6px">Downloading...</h3><p style="color:#8a97ae;margin:0">You can keep using your PC.</p><div class="prog"><i></i></div><div style="display:flex;justify-content:space-between;font-size:13px"><span class="mb"></span><span class="eta" style="color:#8a97ae"></span></div>';
        const t = setInterval(() => { if (!p.isConnected) return clearInterval(t); done = Math.min(total, done + 9 + Math.random() * 8);
          p.querySelector('i').style.width = done / total * 100 + '%'; p.querySelector('.mb').textContent = Math.round(done) + ' MB of ' + total + ' MB';
          p.querySelector('.eta').textContent = done >= total ? 'finishing up...' : 'about ' + Math.max(1, Math.round((total - done) / 55)) + ' s left';
          if (done >= total) { clearInterval(t); setTimeout(() => restart ? boot() : state('done'), 700); } }, 220); };
      state('idle');
    },
    editor(body) { body.innerHTML = '<textarea spellcheck="false">Type here. This is a real text box.\n\nThings to try in this demo:\n- Drag this window by its title bar\n- Open Settings and make the taskbar float\n- Open Update and press Download and restart\n</textarea>'; },
    store(body) {
      const p = el('div', 'pane'); body.appendChild(p);
      [['Steam', 'com.valvesoftware.Steam.png'], ['Spotify', 'com.spotify.Client.png'], ['LibreOffice', 'org.libreoffice.LibreOffice.png'], ['Discord', 'com.discordapp.Discord.png'], ['VLC', 'org.videolan.VLC.png']].forEach(([n, f]) => {
        const b = el('button', 'dbtn alt', 'Install'); b.onclick = () => { b.textContent = 'Installing...'; b.disabled = true; setTimeout(() => { b.textContent = 'Installed'; b.className = 'dbtn'; window.OneClickDemoToast(n + ' is installed', 'Find it in the start menu.'); }, 1100); };
        const r = el('div', 'row', `<div style="display:flex;gap:12px;align-items:center"><img src="${A}${f}" width="34" height="34" alt="">${n}</div>`); r.appendChild(b); p.appendChild(r); });
    },
  };
  function accent(c) { let s = document.getElementById('d-accent'); if (!s) { s = document.head.appendChild(el('style')); s.id = 'd-accent'; }
    s.textContent = `#demo .sw.on,#demo .tb.open::after,#demo .dbtn:not(.alt),#demo .prog i{background:${c}}#demo .side div.on{background:${c};color:#06121f}#demo .menu input:focus{border-color:${c}}`; }

  // ---- restart: plays the start-up animation ----
  function boot() {
    Object.keys(wins).forEach(id => { wins[id].remove(); delete wins[id]; }); pinButtons();
    const b = el('div', 'boot', `<svg viewBox="0 -60 1060 290"><g fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M74 72.5 A76 76 0 1 0 166 72.5" stroke="#2dd4bf" stroke-width="26" data-w="3"/><path d="M250 116 V209" stroke="#fff" stroke-width="24" data-w=".7"/><path d="M250 163 A38 38 0 0 1 326 163 V209" stroke="#fff" stroke-width="24" data-w="1.1"/><path d="M368 163 H460 A46 46 0 1 0 446.5 195.5" stroke="#fff" stroke-width="24" data-w="2"/><path d="M648.2 84.1 A76 76 0 1 0 648.2 181.9" stroke="#fff" stroke-width="24" data-w="2.3"/><path d="M712 57 V209" stroke="#fff" stroke-width="24" data-w=".9"/><path d="M766 116 V209" stroke="#fff" stroke-width="24" data-w=".7"/><path d="M895.2 133.4 A46 46 0 1 0 895.2 192.6" stroke="#fff" stroke-width="24" data-w="1.5"/><path d="M958 57 V209" stroke="#fff" stroke-width="24" data-w=".9"/><path d="M1012 116 L958 168" stroke="#fff" stroke-width="24" data-w=".5"/><path d="M979 148 L1016 209" stroke="#fff" stroke-width="24" data-w=".5"/></g>
      <circle class="o" cx="120" cy="58.5" r="0" fill="#fff"/><ellipse class="i" cx="766" cy="-40" rx="15" ry="15" fill="#2dd4bf" opacity="0"/></svg>`);
    root.appendChild(b);
    window.OneClickWrite(b.querySelector('svg'), () => { b.style.transition = 'opacity .5s'; b.style.opacity = 0; setTimeout(() => { b.remove(); window.OneClickDemoToast('You\u2019re up to date', 'OneClick OS 0.2 is installed.'); }, 500); });
  }
  function reset() { Object.keys(wins).forEach(id => { wins[id].remove(); delete wins[id]; }); root.classList.remove('floating', 'hide'); document.getElementById('d-accent')?.remove(); pinButtons(); }

  // ---- desktop icons, tray pop-ups, notifications ----
  root.querySelectorAll('.dicon').forEach(d => { d.onclick = e => { e.stopPropagation(); root.querySelectorAll('.dicon').forEach(x => x.classList.toggle('sel', x === d)); }; d.ondblclick = () => open(d.dataset.open); });
  const vol = root.querySelector('#d-vol'), cal = root.querySelector('#d-cal');
  const pop = (el, show) => { [vol, cal].forEach(p => p.classList.toggle('show', p === el && (show ?? !el.classList.contains('show')))); };
  root.querySelector('#d-volb').onclick = e => { e.stopPropagation(); pop(vol); };
  vol.onclick = e => e.stopPropagation();
  vol.querySelector('input').oninput = e => root.querySelector('#d-volv').textContent = e.target.value + '%';
  root.querySelector('#d-clock').onclick = e => { e.stopPropagation(); const d = new Date(), y = d.getFullYear(), m = d.getMonth(), first = (new Date(y, m, 1).getDay() + 6) % 7, days = new Date(y, m + 1, 0).getDate();
    let h = '<b>' + d.toLocaleDateString([], { month: 'long', year: 'numeric' }) + '</b><div class="calg">' + ['M','T','W','T','F','S','S'].map(x => '<i>' + x + '</i>').join('') + '<span></span>'.repeat(first);
    for (let i = 1; i <= days; i++) h += '<span' + (i === d.getDate() ? ' class="on"' : '') + '>' + i + '</span>';
    cal.innerHTML = h + '</div>'; pop(cal); };
  root.addEventListener('click', () => { pop(vol, false); root.querySelectorAll('.dicon').forEach(x => x.classList.remove('sel')); });
  window.OneClickDemoToast = (title, text) => { const t = root.querySelector('#d-toast'); t.innerHTML = '<b>' + title + '</b><span>' + text + '</span>'; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 3800); };

  pinButtons(); fillMenu();
})();
