'use strict';
const $ = id => document.getElementById(id);

/* ---------- Icons ---------- */
const ICONS = {
 scan: 'M3 8V5a2 2 0 0 1 2-2h3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0 1-2 2h-3M8 21H5a2 2 0 0 1-2-2v-3M8 12h8M12 8v8',
 upload: 'M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3M12 15V4M7.5 8.5 12 4l4.5 4.5',
 clipboard: 'M9 3h6a1 1 0 0 1 1 1v2H8V4a1 1 0 0 1 1-1ZM8 5H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 12h6M9 16h4',
 pen: 'M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4ZM13.5 6.5l4 4',
 edit: 'M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4ZM13.5 6.5l4 4',
 plus: 'M12 5v14M5 12h14',
 minus: 'M5 12h14',
 grid: 'M5 4h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1ZM15 4h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1ZM5 14h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1ZM15 14h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1Z',
 star: 'm12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z',
 settings: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z',
 trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3',
 copy: 'M9 8h10a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1ZM16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3',
 check: 'm5 12.5 4.5 4.5L19 7',
 checkCircle: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM8 12.5l2.7 2.7L16 9.5',
 info: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM12 11v5M12 8h.01',
 alert: 'M12 4 2.8 19.5h18.4L12 4ZM12 10v4.5M12 17h.01',
 close: 'M6 6l12 12M18 6 6 18',
 search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14ZM16 16l4.5 4.5',
 chevronLeft: 'm14 6-6 6 6 6',
 chevronRight: 'm10 6 6 6-6 6',
 chevronsLeft: 'm11 17-5-5 5-5M18 17l-5-5 5-5',
 chevronsRight: 'm13 17 5-5-5-5M6 17l5-5-5-5',
 refresh: 'M20 11a8 8 0 0 0-14.9-3M4 4v4h4M4 13a8 8 0 0 0 14.9 3M20 20v-4h-4',
 download: 'M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19h14',
 image: 'M5 4h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1ZM4 16l4.5-4.5 3.5 3.5 3-3 5 5M15.5 8.5h.01',
 word: 'M7 3h7l5 5v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1ZM14 3v5h5M9 12l1.5 5 1.5-4 1.5 4 1.5-5',
 sparkles: 'M11 4l1.7 4.8L17.5 10.5l-4.8 1.7L11 17l-1.7-4.8L4.5 10.5l4.8-1.7ZM18.5 15l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8Z',
 sun: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8ZM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
 moon: 'M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z',
};
function icon(name) { return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name] || ICONS.edit}"/></svg>`; }
function setIcon(el, name) { const svg = el.querySelector('svg.icon'); if (svg) svg.outerHTML = icon(name); }
document.querySelectorAll('[data-icon]').forEach(el => el.insertAdjacentHTML('afterbegin', icon(el.dataset.icon)));

/* ---------- State and bridge ---------- */
let bridge = null, rows = [], settings = {}, current = null, dirty = false;
let viewMode = 'rendered', preferredView = 'rendered', galleryMode = 'both', favorites = false, shown = 24;
let previewZoom = 1, previewTimer = 0, renderVersion = 0, renderQueue = Promise.resolve();
let booted = false, systemDark = false, chromeDark = null, lastIndex = 0;
const KIND_NAMES = { formula: '公式', mixed: '图文', text: '文字' };
const COPY_NAMES = { formula: 'LaTeX', mixed: 'Markdown', text: '文本' };

function send(action, values = {}) { if (bridge) bridge.invoke(JSON.stringify({ action, ...values })); }
document.querySelectorAll('[data-action]').forEach(el => el.addEventListener('click', () => send(el.dataset.action)));
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

/* ---------- Feedback: toasts, confirmations, button states ---------- */
function toast(message, kind = 'success', ms) {
 const el = document.createElement('div');
 el.className = 'toast ' + kind;
 el.innerHTML = icon(kind === 'error' ? 'alert' : kind === 'info' ? 'info' : 'checkCircle') + '<span></span>';
 el.lastChild.textContent = message;
 $('toasts').appendChild(el);
 while ($('toasts').children.length > 3) $('toasts').firstChild.remove();
 setTimeout(() => { el.classList.add('leave'); setTimeout(() => el.remove(), 260); }, ms || (kind === 'error' ? 9000 : kind === 'info' ? 4200 : 2400));
}
function ask(title, text, okLabel = '确定', destructive = false) {
 return new Promise(resolve => {
  const dialog = $('ask-dialog');
  $('ask-title').textContent = title; $('ask-text').textContent = text; $('ask-ok').textContent = okLabel;
  $('ask-ok').classList.toggle('destructive', destructive);
  const done = value => { dialog.close(); resolve(value); };
  $('ask-ok').onclick = () => done(true);
  $('ask-cancel').onclick = () => done(false);
  dialog.oncancel = e => { e.preventDefault(); done(false); };
  dialog.showModal(); $('ask-ok').focus();
 });
}
// Runs `then` at once when nothing is unsaved, otherwise after the user agrees to drop the edits.
function leave(then) {
 if (!dirty) { then(); return; }
 ask('放弃未保存的修改？', '当前内容还没有保存，离开后修改会丢失。', '放弃修改', true).then(ok => { if (ok) { dirty = false; then(); } });
}
function flash(el) {
 if (!el) return;
 if (!el.dataset.restore) el.dataset.restore = el.querySelector('svg.icon')?.outerHTML || '';
 setIcon(el, 'check'); el.classList.add('done');
 clearTimeout(el.flashTimer);
 el.flashTimer = setTimeout(() => {
  const svg = el.querySelector('svg.icon');
  if (svg && el.dataset.restore) svg.outerHTML = el.dataset.restore;
  delete el.dataset.restore; el.classList.remove('done');
 }, 1400);
}
function copyText(text, el, label) { send('copy', { text }); flash(el); toast('已复制 ' + label, 'success', 1500); }
function setSegment(id, index) {
 const box = $(id);
 box.style.setProperty('--i', Math.max(0, index));
 box.querySelectorAll('button').forEach((b, i) => b.classList.toggle('selected', i === index));
}
document.addEventListener('pointerdown', e => {
 const button = e.target.closest('.btn,.capture-btn');
 if (!button || button.dataset.tip || button.disabled) return;
 const box = button.getBoundingClientRect(), size = Math.max(box.width, box.height) * 2.2, dot = document.createElement('span');
 dot.className = 'ripple';
 dot.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - box.left - size / 2}px;top:${e.clientY - box.top - size / 2}px`;
 button.appendChild(dot);
 dot.addEventListener('animationend', () => dot.remove());
});

/* ---------- Math rendering ---------- */
function mathTask(fn) { renderQueue = renderQueue.catch(() => {}).then(() => MathJax.startup.promise).then(fn).catch(e => console.error(e)); return renderQueue; }
async function renderMath(el, text, kind, small = false) {
 if (!el.isConnected) return;
 if (kind === 'formula') {
  try {
   const node = await MathJax.tex2svgPromise(text, { display: true });
   // Direct conversion does not install the SVG stylesheet. It also contains
   // the clipping rules that keep screen-reader MathML out of the visual layout.
   const stylesheet = MathJax.svgStylesheet();
   if (!stylesheet.isConnected) document.head.appendChild(stylesheet);
   if (el.isConnected) el.replaceChildren(node);
  } catch (e) { el.innerHTML = `<div class="math-error">${esc(small ? text : '无法预览，请检查 LaTeX：' + e.message)}</div>`; }
 } else {
  const child = document.createElement('div'); child.className = small ? 'card-text' : 'text-preview'; child.textContent = text; el.replaceChildren(child);
  if (kind === 'mixed') { await MathJax.typesetPromise([child]); }
 }
}

/* ---------- Messages from the app ---------- */
function receive(event) {
 const data = JSON.parse(event);
 if (data.type === 'settings') {
  settings = data.settings; systemDark = !!data.system_dark;
  $('shortcut').textContent = settings.hotkey.replaceAll('+', ' ');
  setSegment('quick-mode', ['formula', 'mixed', 'text'].indexOf(settings.mode));
  const off = settings.provider === 'offline';
  $('engine-name').textContent = off ? '离线识别' : settings.provider === 'mathpix' ? 'Mathpix 联网' : '视觉接口 · 联网';
  $('engine-dot').style.background = off ? '' : '#e0a52c';
  $('data-path').textContent = data.data_dir; $('about-version').textContent = data.version;
  applyTheme();
  if (current && !$('detail').hidden) updateFormats();
 } else if (data.type === 'history') {
  const grew = data.rows.length > rows.length;
  rows = data.rows;
  $('nav-count').textContent = rows.length > 99 ? '99+' : rows.length;
  $('nav-count').toggleAttribute('data-zero', !rows.length);
  if (grew && booted) { $('nav-count').classList.remove('bump'); void $('nav-count').offsetWidth; $('nav-count').classList.add('bump'); }
  if (!$('library').hidden) renderGallery();
  updateChrome();
  // Open on the latest snip, the way a snipping tool is normally used.
  if (!booted) { booted = true; if (rows.length) send('detail', { id: rows[0].id }); }
 } else if (data.type === 'detail') {
  if (dirty) { toast('新结果已存入资料库，当前编辑内容已保留。', 'info'); return; }
  current = data.row; showDetail();
 } else if (data.type === 'toast') { toast(data.message, data.kind); }
 else if (data.type === 'busy') {
  $('progress').hidden = false; $('progress-label').textContent = data.message;
  if (data.preview !== undefined) $('progress-image').src = data.preview;
  $('queue-label').textContent = data.remaining ? '另有 ' + data.remaining + ' 项等待中' : '较复杂的公式需要更多时间';
 } else if (data.type === 'idle') { $('progress').hidden = true; $('progress-image').removeAttribute('src'); }
 else if (data.type === 'deleted') {
  if (current?.id !== data.id) return;
  dirty = false; current = null;
  const next = rows[Math.min(lastIndex, rows.length - 1)];
  if (next && !$('detail').hidden) send('detail', { id: next.id }); else showLibrary(favorites);
 } else if (data.type === 'favorite') { if (current?.id === data.id) { current.favorite = data.value; updateFavorite(); } }
 else if (data.type === 'tidied') {
  if (data.text === $('editor').value) { toast('内容已经很整洁了', 'info', 1800); return; }
  $('editor').value = data.text; markDirty(); renderPreview(); updateFormats(); toast('已整理', 'success', 1500);
 }
}

/* ---------- Toolbar state ---------- */
function updateChrome() {
 const inDetail = !$('detail').hidden;
 const index = current?.id ? rows.findIndex(r => r.id === current.id) : -1;
 const label = !inDetail ? rows.length + ' 条' : index >= 0 ? (rows.length - index) + ' / ' + rows.length : '新建';
 const position = $('detail-position');
 if (position.textContent !== label) { position.textContent = label; position.classList.remove('tick'); void position.offsetWidth; position.classList.add('tick'); }
 const buttons = $('pager').querySelectorAll('button');
 const older = inDetail && index >= 0 ? index < rows.length - 1 : rows.length > 0, newer = inDetail && index >= 0 ? index > 0 : rows.length > 0;
 buttons[0].disabled = buttons[1].disabled = !older; buttons[2].disabled = buttons[3].disabled = !newer;
 $('delete-button').disabled = !(inDetail && current?.id);
 $('nav-library').classList.toggle('active', !inDetail);
 $('confidence').hidden = !(inDetail && current && current.confidence != null);
}
// Records are stored newest first; the pager counts upwards so the newest is N / N.
function navigateRecord(delta) {
 if (!rows.length) return;
 const index = current?.id ? rows.findIndex(r => r.id === current.id) : -1;
 const target = index < 0 ? 0 : $('detail').hidden ? index : index - delta;
 if (rows[target]) openRecord(rows[target].id);
}
function jumpRecord(end) { if (rows.length) openRecord(rows[end === 'newest' ? 0 : rows.length - 1].id); }
function openRecord(id) { leave(() => send('detail', { id })); }
function toggleLibrary() {
 if ($('library').hidden) { showLibrary(favorites); return; }
 if (!current) return;
 $('library').hidden = true; $('detail').hidden = false; updateChrome();
}

/* ---------- Library ---------- */
function showLibrary(star = false) {
 leave(() => {
  $('detail').hidden = true; $('library').hidden = false; favorites = star; shown = 24;
  setSegment('library-filter', star ? 1 : 0);
  renderGallery(); updateChrome();
 });
}
function shortDate(s) { const d = new Date(s); if (Number.isNaN(d.getTime())) return ''; return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }); }
function engineName(engine) { return engine?.startsWith('联网') ? '联网识别' : engine?.startsWith('离线') ? '离线识别' : '手动编辑'; }
function renderGallery() {
 const q = $('search').value.trim().toLowerCase();
 const filtered = rows.filter(r => (!favorites || r.favorite) && (!q || (r.title + ' ' + r.content).toLowerCase().includes(q)));
 $('result-count').textContent = (favorites ? '已收藏' : '全部记录') + ' · ' + filtered.length; $('empty').hidden = filtered.length !== 0;
 if (!filtered.length) {
  const fresh = !rows.length;
  $('empty').querySelector('h2').textContent = q ? '没有匹配的记录' : favorites ? '把常用公式收进这里' : '你的第一条公式，从这里开始';
  $('empty').querySelector('p').textContent = q ? '换个关键词试试。' : favorites ? '点记录上的星标即可收藏。' : '框选屏幕上的公式，或把图片直接拖进窗口。';
  $('empty').querySelector('.empty-actions').hidden = $('empty').querySelector('.empty-tips').hidden = !fresh;
 }
 $('gallery').replaceChildren(); $('load-more').hidden = filtered.length <= shown;
 filtered.slice(0, shown).forEach((r, i) => {
  const el = document.createElement('article'); el.className = 'snip-card'; el.tabIndex = 0; el.setAttribute('aria-label', '打开 ' + r.title);
  el.style.animationDelay = Math.min(i, 12) * 28 + 'ms';
  el.innerHTML = `<div class="card-heading"><span class="pill ${r.kind}">${KIND_NAMES[r.kind] || '公式'}</span><b title="${esc(r.title)}">${esc(r.title)}</b><button class="icon-btn ${r.favorite ? 'starred' : ''}" aria-label="收藏">${icon('star')}</button></div>`;
  el.querySelector('button').onclick = e => { e.stopPropagation(); send('favorite', { id: r.id }); };
  if (galleryMode !== 'rendered') { const original = document.createElement('div'); original.className = 'card-original'; original.innerHTML = r.thumbnail ? `<img src="${r.thumbnail}" alt="原始图片" loading="lazy">` : `<span class="no-image">${r.image ? '打开查看原图' : '手动创建 · 无原始图片'}</span>`; el.appendChild(original); }
  if (galleryMode !== 'original') { const formula = document.createElement('div'); formula.className = 'card-formula'; formula.textContent = r.content; el.appendChild(formula); mathTask(() => renderMath(formula, r.content, r.kind, true)); }
  const foot = document.createElement('div'); foot.className = 'card-footer';
  foot.innerHTML = `<span>${shortDate(r.created)} · ${engineName(r.engine)}</span><button class="icon-btn card-copy" aria-label="复制">${icon('copy')}</button>`;
  foot.querySelector('button').onclick = e => { e.stopPropagation(); copyText(r.content, e.currentTarget, COPY_NAMES[r.kind] || 'LaTeX'); };
  el.appendChild(foot);
  el.onclick = () => openRecord(r.id); el.onkeydown = e => { if (e.key === 'Enter' && e.target === el) openRecord(r.id); }; $('gallery').appendChild(el);
 });
}
function galleryView(mode, btn) { galleryMode = mode; setSegment('gallery-view', [...btn.parentNode.querySelectorAll('button')].indexOf(btn)); renderGallery(); }

/* ---------- Snip view ---------- */
function newSnippet(example = false) {
 leave(() => {
  current = { id: null, title: example ? '二次方程求根公式 · 编辑示例' : '新建公式', content: example ? String.raw`x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}` : '', kind: 'formula', engine: '手动编辑', confidence: null, original: '', favorite: 0 };
  showDetail(); if (example) markDirty(); $('editor').focus();
 });
}
function showDetail() {
 $('library').hidden = true; $('detail').hidden = false; $('record-title').value = current.title; $('editor').value = current.content; $('content-kind').value = current.kind;
 const meta = [current.created ? shortDate(current.created) : '未保存', engineName(current.engine), current.elapsed ? current.elapsed.toFixed(1) + ' 秒' : ''].filter(Boolean);
 $('record-meta').innerHTML = meta.map(m => `<span>${esc(m)}</span>`).join('');
 $('original-image').src = current.original || ''; $('tab-original').disabled = !current.original; $('tab-both').disabled = !current.original; $('retry-button').hidden = !current.original; $('export-original').hidden = !current.original;
 const score = current.confidence == null ? 0 : Math.round(current.confidence * 100);
 $('confidence').className = 'confidence' + (score >= 90 ? '' : score >= 70 ? ' mid' : ' low');
 $('confidence-value').textContent = score + '%'; $('confidence-fill').style.width = '0';
 requestAnimationFrame(() => requestAnimationFrame(() => { $('confidence-fill').style.width = score + '%'; }));
 dirty = false; $('draft-state').textContent = ''; $('save-button').classList.remove('primary');
 const index = rows.findIndex(r => r.id === current.id); if (index >= 0) lastIndex = index;
 previewZoom = 1; zoom(0); updateFavorite(); previewView(current.original ? preferredView : 'rendered', false); updateFormats(); renderPreview(); updateChrome();
}
function updateFavorite() { $('star-button').classList.toggle('starred', !!current?.favorite); $('star-button').disabled = !current?.id; $('star-button').dataset.tip = current?.favorite ? '取消收藏' : '收藏'; }
function favoriteCurrent() { if (current?.id) send('favorite', { id: current.id }); }
function markDirty() { dirty = true; $('draft-state').textContent = '● 未保存'; $('save-button').classList.add('primary'); }
function livePreview() { clearTimeout(previewTimer); previewTimer = setTimeout(() => { renderPreview(); updateFormats(); }, 330); }
function renderPreview() {
 const version = ++renderVersion; const text = $('editor').value; const kind = $('content-kind').value;
 document.querySelectorAll('.formula-only').forEach(el => el.hidden = kind !== 'formula');
 $('tidy-button').hidden = kind === 'text';
 $('copy-main').querySelector('span').textContent = '复制 ' + COPY_NAMES[kind];
 mathTask(() => { if (version !== renderVersion) return; return renderMath($('rendered-content'), text, kind); });
}
function updateFormats() {
 const t = $('editor').value, k = $('content-kind').value;
 const list = k === 'formula'
  ? [['latex', 'LaTeX', t], ['inline', '$ … $', '$' + t + '$'], ['display', '$$ … $$', '$$\n' + t + '\n$$'], ['bracket', '\\[ … \\]', '\\[\n' + t + '\n\\]'], ['equation', 'equation', '\\begin{equation}\n' + t + '\n\\end{equation}']]
  : [['latex', COPY_NAMES[k], t]];
 $('formats').replaceChildren(); $('lower').classList.toggle('single', list.length === 1);
 list.forEach(([key, label, text]) => {
  const row = document.createElement('div'); row.className = 'format-row'; row.title = '点击复制';
  const auto = k === 'formula' && settings.auto_copy !== false && (settings.copy_format || 'latex') === key;
  row.innerHTML = `<span class="format-tag">${esc(label)}</span><code>${esc(text)}</code>${auto ? '<span class="auto">自动复制</span>' : ''}<button class="icon-btn" aria-label="复制 ${esc(label)}">${icon('copy')}</button>`;
  row.onclick = () => { copyText(text, row.querySelector('button'), label); row.classList.add('done'); setTimeout(() => row.classList.remove('done'), 700); };
  $('formats').appendChild(row);
 });
}
function previewView(mode, remember = true) {
 viewMode = mode; if (remember) preferredView = mode;
 $('original-pane').hidden = mode === 'rendered'; $('rendered-pane').hidden = mode === 'original';
 setSegment('preview-tabs', ['rendered', 'original', 'both'].indexOf(mode));
}
function zoom(delta, reset = false) {
 previewZoom = reset ? 1 : Math.max(.4, Math.min(2.5, previewZoom + delta));
 $('zoom-label').textContent = Math.round(previewZoom * 100) + '%'; $('rendered-content').style.fontSize = 24 * previewZoom + 'px';
 // Up to 100% a wide formula shrinks to fit the pane; zooming in lets it scroll instead.
 $('rendered-content').classList.toggle('fit', previewZoom <= 1);
}
function saveCurrent() {
 const content = $('editor').value.trim(); if (!content) { toast('请先输入内容。', 'info'); return false; }
 dirty = false; send('save', { id: current?.id, title: $('record-title').value.trim() || '未命名公式', content, kind: $('content-kind').value }); return true;
}
function tidyCurrent() { if ($('editor').value.trim()) send('tidy', { text: $('editor').value, kind: $('content-kind').value }); }
function copyMain(el) { const text = $('editor').value; if (!text.trim()) { toast('还没有内容可复制。', 'info'); return; } copyText(text, el, COPY_NAMES[$('content-kind').value]); }
function toggleExport(e) { e.stopPropagation(); $('export-menu').hidden = !$('export-menu').hidden; }
document.addEventListener('click', e => { if (!e.target.closest('.dropdown')) $('export-menu').hidden = true; });
// Copying and exporting read the saved record, so pending edits are saved first.
async function exportCurrent(format, el) {
 $('export-menu').hidden = true;
 if (!current?.id) { toast('请先保存，再复制或导出。', 'info'); return; }
 if (dirty) { clearTimeout(previewTimer); renderPreview(); }
 let svg = ''; if (['png', 'svg', 'copy_png'].includes(format)) {
  await renderQueue; const node = $('rendered-content').querySelector('svg'); if (!node) { toast('当前预览没有可导出的公式图像。', 'error'); return; }
  const clone = node.cloneNode(true); let rect = node.getBoundingClientRect();
  // Hidden panes have no screen size. MathJax SVG width/height in ex remains valid after conversion.
  const ex = parseFloat(getComputedStyle($('rendered-content')).fontSize) * .5;
  clone.setAttribute('width', String(rect.width || parseFloat(node.getAttribute('width')) * ex)); clone.setAttribute('height', String(rect.height || parseFloat(node.getAttribute('height')) * ex)); clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg'); clone.style.color = '#213b30'; clone.setAttribute('color', '#213b30');
  svg = new XMLSerializer().serializeToString(clone).replaceAll('currentColor', '#213b30');
 }
 if (dirty && !saveCurrent()) return;
 send('export', { id: current.id, format, svg }); if (format === 'copy_png') flash(el);
}
function copyMathML(el) {
 if (!current?.id) { toast('请先保存，再复制或导出。', 'info'); return; }
 if (dirty && !saveCurrent()) return;
 send('copy_mathml', { id: current.id }); flash(el);
}
function deleteCurrent() {
 if (!current?.id || $('detail').hidden) return;
 const id = current.id;
 ask('删除这条记录？', '识别结果和原图会一起删除，无法恢复。', '删除', true).then(ok => { if (ok) { dirty = false; send('delete', { id }); } });
}
function retryCurrent() { if (current?.id) leave(() => send('retry', { id: current.id })); }

/* ---------- Mode, theme, settings ---------- */
function quickMode(mode) { settings.mode = mode; setSegment('quick-mode', ['formula', 'mixed', 'text'].indexOf(mode)); send('quick', { key: 'mode', value: mode }); }
function isDark() { const theme = settings.theme || 'auto'; return theme === 'dark' || (theme === 'auto' && systemDark); }
function applyTheme() {
 const dark = isDark();
 document.documentElement.dataset.theme = dark ? 'dark' : 'light';
 setIcon($('theme-button'), dark ? 'sun' : 'moon');
 if (chromeDark !== dark) { chromeDark = dark; send('chrome', { dark }); }
}
function toggleTheme() {
 const next = isDark() ? 'light' : 'dark';
 const box = $('theme-button').getBoundingClientRect();
 document.documentElement.style.setProperty('--vx', box.left + box.width / 2 + 'px');
 document.documentElement.style.setProperty('--vy', box.top + box.height / 2 + 'px');
 const change = () => { settings.theme = next; applyTheme(); };
 if (document.startViewTransition) document.startViewTransition(change); else change();
 send('quick', { key: 'theme', value: next });
}
function openSettings() {
 $('setting-provider').value = settings.provider || 'offline'; $('setting-mode').value = settings.mode || 'formula'; $('setting-hotkey').value = settings.hotkey || 'Ctrl+Alt+S'; $('setting-autocopy').checked = settings.auto_copy !== false; $('setting-tray').checked = settings.close_to_tray !== false;
 $('setting-theme').value = settings.theme || 'auto'; $('setting-copyformat').value = settings.copy_format || 'latex'; $('setting-tidy').checked = settings.tidy !== false;
 $('setting-appid').value = settings.mathpix_id || ''; $('setting-endpoint').value = settings.endpoint || ''; $('setting-model').value = settings.model || ''; $('setting-key').value = ''; $('setting-clear-key').checked = false;
 providerFields(); $('settings-dialog').showModal();
}
function closeSettings() { $('setting-key').value = ''; $('settings-dialog').close(); }
function providerFields() { const p = $('setting-provider').value; $('cloud-fields').hidden = p === 'offline'; $('offline-fields').hidden = p !== 'offline'; $('appid-field').hidden = p !== 'mathpix'; $('compatible-fields').hidden = p !== 'compatible'; $('setting-key').placeholder = (p === settings.provider && settings.has_key) ? '已保存密钥；留空保留' : '输入 API 密钥（本地视觉服务可留空）'; }
function saveSettings() {
 const cfg = { provider: $('setting-provider').value, mode: $('setting-mode').value, hotkey: $('setting-hotkey').value, auto_copy: $('setting-autocopy').checked, close_to_tray: $('setting-tray').checked, theme: $('setting-theme').value, copy_format: $('setting-copyformat').value, tidy: $('setting-tidy').checked, mathpix_id: $('setting-appid').value.trim(), endpoint: $('setting-endpoint').value.trim(), model: $('setting-model').value.trim(), api_key: $('setting-key').value.trim(), clear_key: $('setting-clear-key').checked };
 send('settings', { settings: cfg }); closeSettings();
}

/* ---------- Keyboard ---------- */
document.addEventListener('keydown', e => {
 if (document.querySelector('dialog[open]')) return;
 const editable = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName), key = e.key.toLowerCase(), inDetail = !$('detail').hidden;
 if (e.ctrlKey && key === 'f') { e.preventDefault(); showLibrary(favorites); if (!$('library').hidden) $('search').focus(); }
 else if (e.ctrlKey && e.key === 'Enter' && inDetail) { e.preventDefault(); saveCurrent(); }
 else if (e.ctrlKey && key === 'v' && !editable) { e.preventDefault(); send('paste'); }
 else if (e.ctrlKey && key === 'o') { e.preventDefault(); send('import'); }
 else if (e.ctrlKey && key === 'n') { e.preventDefault(); newSnippet(); }
 else if (e.ctrlKey && key === 'l') { e.preventDefault(); toggleLibrary(); }
 else if (e.ctrlKey && key === 'c' && !editable && inDetail && !String(getSelection())) { e.preventDefault(); copyMain($('copy-main')); }
 else if (!editable && !e.ctrlKey && !e.altKey && e.key === 'ArrowLeft') navigateRecord(-1);
 else if (!editable && !e.ctrlKey && !e.altKey && e.key === 'ArrowRight') navigateRecord(1);
 else if (!editable && e.key === 'Delete') deleteCurrent();
 else if (e.key === 'Escape') { if (!$('export-menu').hidden) $('export-menu').hidden = true; else if (editable) e.target.blur(); }
});
window.addEventListener('dragover', e => e.preventDefault()); window.addEventListener('drop', e => e.preventDefault());
setSegment('library-filter', 0); setSegment('gallery-view', 0); setSegment('preview-tabs', 0); updateChrome();
new QWebChannel(qt.webChannelTransport, channel => { bridge = channel.objects.bridge; bridge.event.connect(receive); send('ready'); });
