'use strict';
// ════════════════════════════════════════════════════════
// Video Autopilot — Dashboard JS
// Vanilla, no build step, no external deps.
// ════════════════════════════════════════════════════════

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

// ── api helper ───────────────────────────────────────────
async function api(path, opts = {}) {
  const r = await fetch('/api' + path, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
  return data;
}

// ── niche colours ────────────────────────────────────────
const NICHE_COLOR = {
  motivation:'#f472b6', finance:'#4ade80', money:'#4ade80',
  psychology:'#60a5fa', history:'#fb923c', ai:'#a78bfa',
  tech:'#a78bfa', health:'#2dd4bf', mystery:'#f87171',
  stoic:'#94a3b8', business:'#fbbf24', facts:'#60a5fa',
  default:'#7c5cf6',
};
const nicheColor = (niche='') =>
  NICHE_COLOR[niche.toLowerCase()] || NICHE_COLOR.default;

// ── toast ────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const icons = { success:'✓', error:'✗', info:'→' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span class="toast-icon">${icons[type]??'•'}</span>
    <span class="toast-body">${esc(msg)}</span>
    <button class="toast-close">✕</button>`;
  $('#toastStack').prepend(t);
  const close = () => { t.classList.add('out'); setTimeout(() => t.remove(), 260); };
  t.querySelector('.toast-close').onclick = close;
  setTimeout(close, 4500);
}

// ── navigation ───────────────────────────────────────────
const VIEWS = {};
$$('.nav-item').forEach(item => {
  item.addEventListener('click', () => navigateTo(item.dataset.view));
});

function navigateTo(name) {
  $$('.nav-item').forEach(i => i.classList.toggle('active', i.dataset.view === name));
  $$('.view').forEach(v => v.classList.toggle('active', v.id === `view-${name}`));
  VIEWS[name]?.();
}
window.navigateTo = navigateTo;

// ════════════════════════════════════════════════════════
// DASHBOARD
// ════════════════════════════════════════════════════════
let channelData = [];

async function loadDashboard() {
  const [analytics, envSt] = await Promise.all([
    api('/analytics').catch(() => ({ total_videos:0, channels:{}, recent_runs:[] })),
    api('/env-status').catch(() => ({})),
  ]);

  renderStats(analytics);
  renderSetupBanner(envSt, analytics);
  renderActivity(analytics.recent_runs);
  renderQuickChannels();
  loadSidebarKeys(envSt);
}

function animateNum(el, to) {
  const dur = 700, start = performance.now();
  const tick = now => {
    const p = Math.min(1, (now - start) / dur);
    el.textContent = Math.round(p * to);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function renderStats(a) {
  const items = [
    { icon:'🎬', label:'Videos produced', value: a.total_videos,      cls:'purple' },
    { icon:'📺', label:'Active channels',  value: Object.keys(a.channels).length, cls:'cyan' },
    { icon:'🚀', label:'Published',        value: a.recent_runs.filter(r=>r.status==='posted').length, cls:'green' },
    { icon:'⚡', label:'Dry-runs built',   value: a.recent_runs.filter(r=>r.status==='dry_run').length, cls:'orange' },
  ];
  $('#statsRow').innerHTML = items.map(it =>
    `<div class="stat-card">
      <div class="stat-icon ${it.cls}">${it.icon}</div>
      <div class="stat-num" data-val="${it.value}">0</div>
      <div class="stat-lbl">${esc(it.label)}</div>
    </div>`).join('');
  $$('.stat-num').forEach(el => animateNum(el, +el.dataset.val));
}

function renderSetupBanner(env, analytics) {
  const hasLLM     = env.ANTHROPIC_API_KEY || env.OPENAI_API_KEY;
  const hasVisuals = env.PEXELS_API_KEY || env.FAL_KEY || env.REPLICATE_API_TOKEN;
  const hasVideos  = analytics.total_videos > 0;
  const hasPublish = env.AYRSHARE_API_KEY || env.UPLOAD_POST_API_KEY;

  const steps = [
    { title: 'Add an LLM key', desc: 'Claude (Anthropic) or OpenAI — powers idea generation & scripting. Paste into your .env file.', done: !!hasLLM, action: 'settings' },
    { title: 'Add a Pexels key (free)', desc: 'Free stock B-roll for your videos. Sign up at pexels.com/api — takes 60 seconds.', done: !!hasVisuals, action: 'settings' },
    { title: 'Generate your first video', desc: 'Go to Generate → pick a channel → keep Dry-run ON → hit Start. A video appears in Library.', done: hasVideos, action: 'generate' },
    { title: 'Connect a publish provider', desc: 'Ayrshare posts to YouTube, TikTok, Instagram & Facebook with a single API token.', done: !!hasPublish, action: 'settings' },
  ];

  const done = steps.filter(s => s.done).length;
  const banner = $('#setupBanner');
  if (done === steps.length) { banner.style.display = 'none'; return; }
  banner.style.display = '';
  $('#setupProgress').textContent = `${done} of ${steps.length} complete`;
  $('#setupSteps').innerHTML = steps.map(s =>
    `<div class="setup-step ${s.done?'done':''}" data-action="${s.action}">
      <div class="step-check">${s.done?'✓':''}</div>
      <div class="step-info">
        <div class="step-title">${esc(s.title)}</div>
        <div class="step-desc">${esc(s.desc)}</div>
      </div>
    </div>`).join('');
  $$('.setup-step').forEach(el => {
    el.addEventListener('click', () => navigateTo(el.dataset.action));
  });
}

function renderActivity(runs) {
  const feed = $('#activityFeed');
  if (!runs?.length) {
    feed.innerHTML = `<div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <h4>No activity yet</h4>
      <p>Generate your first video to see it here.</p>
    </div>`;
    return;
  }
  feed.innerHTML = runs.slice(0,14).map(r =>
    `<div class="activity-item">
      <div class="activity-dot ${r.status}"></div>
      <div class="activity-body">
        <div class="activity-title">${esc(r.title || r.slug || r.channel)}</div>
        <div class="activity-meta">${esc(r.channel)} · ${esc(r.status)}</div>
      </div>
      <span class="status-pill ${r.status}">${esc(r.status)}</span>
    </div>`).join('');
}

function renderQuickChannels() {
  const qc = $('#quickChannels');
  if (!channelData.length) { qc.innerHTML = '<div class="empty-state"><p>No channels configured</p></div>'; return; }
  qc.innerHTML = channelData.map(c =>
    `<div class="quick-ch" data-key="${esc(c.key)}">
      <div class="quick-ch-dot" style="background:${nicheColor(c.niche)}"></div>
      <div class="quick-ch-info">
        <div class="quick-ch-name">${esc(c.name)}</div>
        <div class="quick-ch-sub">${esc(c.niche)} · ${c.produced} videos</div>
      </div>
      <button class="quick-ch-btn">▶ Run</button>
    </div>`).join('');
  $$('.quick-ch').forEach(el => {
    el.addEventListener('click', () => quickGenerate(el.dataset.key));
  });
}

function loadSidebarKeys(env) {
  const labels = {
    ANTHROPIC_API_KEY:'Claude', OPENAI_API_KEY:'OpenAI',
    PEXELS_API_KEY:'Pexels', ELEVENLABS_API_KEY:'ElevenLabs',
    AYRSHARE_API_KEY:'Ayrshare',
  };
  $('#sidebarKeys').innerHTML =
    `<div class="sidebar-keys-title">API Keys</div>` +
    Object.entries(labels).map(([k,l]) =>
      `<div class="key-row">
        <span>${l}</span>
        <span class="key-dot ${env[k]?'on':'off'}"></span>
      </div>`).join('');
}

$('#refreshDash').addEventListener('click', loadDashboard);
$('#quickGenBtn').addEventListener('click', () => navigateTo('generate'));

// ════════════════════════════════════════════════════════
// GENERATE
// ════════════════════════════════════════════════════════
let selectedChannel = null;
let genCount = 1;
let activeJobId = null;
let pollTimer = null;

const STAGES = ['ideation','script','voiceover','visuals','captions','assemble','metadata','publish'];
const STAGE_PATTERNS = {
  ideation:  /ideation|idea:/i,
  script:    /script:|scriptwriter/i,
  voiceover: /voiceover:|voice\.mp3/i,
  visuals:   /visuals:|clips downloaded/i,
  captions:  /captions:|captions\.ass/i,
  assemble:  /assemble:|final\.mp4/i,
  metadata:  /metadata:|title:/i,
  publish:   /publish|posting|posted|dry.run/i,
};

function renderGenChannelPicker() {
  const picker = $('#genChannelPicker');
  picker.innerHTML = channelData.map(c =>
    `<div class="ch-pick ${c.key===selectedChannel?'selected':''}" data-key="${esc(c.key)}">
      <div class="ch-pick-dot" style="background:${nicheColor(c.niche)}"></div>
      <span class="ch-pick-name">${esc(c.name)}</span>
      <span class="ch-pick-niche">${esc(c.niche)}</span>
    </div>`).join('');
  $$('.ch-pick').forEach(el => {
    el.addEventListener('click', () => {
      selectedChannel = el.dataset.key;
      $$('.ch-pick').forEach(p => p.classList.toggle('selected', p.dataset.key===selectedChannel));
      if ($('#genAll').checked) $('#genAll').click(); // uncheck all
    });
  });
  if (!selectedChannel && channelData.length) selectedChannel = channelData[0].key;
  $$('.ch-pick').forEach(p => p.classList.toggle('selected', p.dataset.key===selectedChannel));
}

// count buttons
$('#countDown').addEventListener('click', () => {
  if (genCount > 1) { genCount--; $('#countVal').textContent = genCount; }
});
$('#countUp').addEventListener('click', () => {
  if (genCount < 10) { genCount++; $('#countVal').textContent = genCount; }
});

$('#genAll').addEventListener('change', e => {
  const on = e.target.checked;
  $('#countDown').disabled = on;
  $('#countUp').disabled = on;
  $$('.ch-pick').forEach(el => el.style.opacity = on ? '0.4' : '1');
});

$('#clearLog').addEventListener('click', () => {
  $('#logOutput').textContent = 'Log cleared.';
  resetStages();
});

function resetStages() {
  $$('.stage').forEach(s => s.className = 'stage');
}

function setStage(name, state) {
  const el = $(`.stage[data-stage="${name}"]`);
  if (el) el.className = `stage ${state}`;
}

function updateStagesFromLog(logs) {
  let lastDone = -1;
  STAGES.forEach((s, i) => {
    const matched = logs.some(l => STAGE_PATTERNS[s]?.test(l));
    if (matched) lastDone = i;
  });
  STAGES.forEach((s, i) => {
    if (i < lastDone) setStage(s, 'done');
    else if (i === lastDone) setStage(s, 'done');
    else if (i === lastDone + 1) setStage(s, 'active');
    else setStage(s, '');
  });
}

$('#genBtn').addEventListener('click', async () => {
  const allChannels = $('#genAll').checked;
  if (!allChannels && !selectedChannel) { toast('Pick a channel first', 'error'); return; }

  $('#genBtn').disabled = true;
  resetStages();
  setStage('ideation', 'active');
  $('#logOutput').textContent = 'Starting pipeline…\n';
  $('#logStatus').className = 'status-pill running';
  $('#logStatus').textContent = 'running';
  $('#logTitle').textContent = `Live log — ${allChannels ? 'all channels' : selectedChannel}`;

  try {
    const { job_id } = await api('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: selectedChannel,
        count: genCount,
        dry_run: $('#genDry').checked,
        all_channels: allChannels,
      }),
    });
    activeJobId = job_id;
    updateRunningBadge(true);
    pollJob(job_id);
  } catch(e) {
    toast('Failed to start: ' + e.message, 'error');
    $('#genBtn').disabled = false;
    setLogStatus('error');
  }
});

function setLogStatus(st) {
  $('#logStatus').className = `status-pill ${st}`;
  $('#logStatus').textContent = st;
}

function pollJob(jid) {
  clearInterval(pollTimer);
  const logEl = $('#logOutput');

  const tick = async () => {
    try {
      const j = await api(`/jobs/${jid}`);
      const atBottom = logEl.scrollHeight - logEl.scrollTop - logEl.clientHeight < 60;
      logEl.textContent = j.logs.join('\n');
      if (atBottom) logEl.scrollTop = logEl.scrollHeight;

      updateStagesFromLog(j.logs);

      if (j.status !== 'running') {
        clearInterval(pollTimer);
        activeJobId = null;
        updateRunningBadge(false);
        setLogStatus(j.status);
        $('#genBtn').disabled = false;

        if (j.status === 'done') {
          STAGES.forEach(s => setStage(s, 'done'));
          toast('Video generated successfully!', 'success');
          loadLibraryData(); // refresh library
        } else {
          toast('Pipeline encountered an error — check the log', 'error');
        }
      }
    } catch {
      clearInterval(pollTimer);
      $('#genBtn').disabled = false;
    }
  };

  tick();
  pollTimer = setInterval(tick, 1800);
}

function updateRunningBadge(on) {
  const b = $('#runningBadge');
  b.style.display = on ? '' : 'none';
  if (on) b.textContent = '•';
}

function quickGenerate(channelKey) {
  navigateTo('generate');
  selectedChannel = channelKey;
  renderGenChannelPicker();
  setTimeout(() => $('#genBtn').click(), 120);
}

// ════════════════════════════════════════════════════════
// LIBRARY
// ════════════════════════════════════════════════════════
let libraryItems = [];
let libSearch = '';
let libFilter = '';

async function loadLibraryData() {
  libraryItems = await api('/library').catch(() => []);
  renderLibrary();
  populateLibFilter();
}

function populateLibFilter() {
  const channels = [...new Set(libraryItems.map(i => i.channel).filter(Boolean))];
  const sel = $('#libFilter');
  const cur = sel.value;
  sel.innerHTML = `<option value="">All channels</option>` +
    channels.map(c => `<option value="${esc(c)}" ${c===cur?'selected':''}>${esc(c)}</option>`).join('');
}

function renderLibrary() {
  const grid = $('#libraryGrid');
  let items = libraryItems;
  if (libSearch) items = items.filter(i => i.title.toLowerCase().includes(libSearch.toLowerCase()));
  if (libFilter) items = items.filter(i => i.channel === libFilter);

  if (!items.length) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;padding:80px 24px">
      <div class="empty-state-icon">🎞️</div>
      <h4>${libSearch||libFilter ? 'No matches found' : 'No videos yet'}</h4>
      <p>${libSearch||libFilter ? 'Try a different search or filter.' : 'Generate your first video — hit the Generate tab above!'}</p>
    </div>`;
    return;
  }

  grid.innerHTML = items.map(it => {
    const color = nicheColor(it.niche || it.channel);
    return `<div class="video-card" data-rel="${esc(it.rel)}">
      <div class="video-thumb">
        ${it.has_video
          ? `<img src="/api/thumbnail/${it.rel}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'video-thumb-placeholder\\'><div class=\\'thumb-icon\\'>🎬</div><div>No thumbnail</div></div><div class=\\'thumb-play\\'><div class=\\'thumb-play-btn\\'><svg viewBox=\\'0 0 24 24\\' width=\\'22\\' height=\\'22\\' fill=\\'white\\'><polygon points=\\'5 3 19 12 5 21 5 3\\'/></svg></div></div>'">`
          : `<div class="video-thumb-placeholder"><div class="thumb-icon">⏳</div><div>Processing</div></div>`}
        ${it.has_video ? `<div class="thumb-play"><div class="thumb-play-btn"><svg viewBox="0 0 24 24" width="22" height="22" fill="white"><polygon points="5 3 19 12 5 21 5 3"/></svg></div></div>` : ''}
      </div>
      <div class="video-card-body">
        <div class="video-card-ch" style="color:${color}">${esc(it.channel)}</div>
        <div class="video-card-title">${esc(it.title)}</div>
        <div class="video-card-meta">
          <span class="video-card-date">${esc(it.date)}</span>
          <button class="video-card-del" data-rel="${esc(it.rel)}" title="Delete" onclick="event.stopPropagation()">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
          </button>
        </div>
      </div>
    </div>`;
  }).join('');

  $$('.video-card').forEach(card => {
    card.addEventListener('click', () => openVideoModal(card.dataset.rel));
  });
  $$('.video-card-del').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (!confirm('Delete this video?')) return;
      try {
        await api(`/library/${btn.dataset.rel}`, { method: 'DELETE' });
        toast('Video deleted', 'info');
        await loadLibraryData();
      } catch(err) { toast('Delete failed: ' + err.message, 'error'); }
    });
  });
}

$('#libSearch').addEventListener('input', e => { libSearch = e.target.value; renderLibrary(); });
$('#libFilter').addEventListener('change', e => { libFilter = e.target.value; renderLibrary(); });

async function openVideoModal(rel) {
  const modal = $('#videoModal');
  $('#modalVideo').src = `/api/video/${rel}`;
  modal.classList.add('open');
  try {
    const m = await api(`/library/${rel}/meta`);
    const md = m.metadata || {};
    const tags = (md.hashtags || []).map(t => `<span class="modal-tag">${esc(t)}</span>`).join('');
    $('#modalInfo').innerHTML = `
      <h4>${esc(md.title || 'Untitled')}</h4>
      <p>${esc(md.description || '')}</p>
      ${tags ? `<div class="modal-tags">${tags}</div>` : ''}
      ${md.pinned_comment ? `<p class="text-muted text-sm mt-12"><b>Pinned comment:</b> ${esc(md.pinned_comment)}</p>` : ''}`;
  } catch { $('#modalInfo').innerHTML = ''; }
}

$('#modalClose').addEventListener('click', () => {
  $('#videoModal').classList.remove('open');
  $('#modalVideo').pause();
  $('#modalVideo').src = '';
});
$('#videoModal').addEventListener('click', e => {
  if (e.target === $('#videoModal')) $('#modalClose').click();
});

// ════════════════════════════════════════════════════════
// CHANNELS
// ════════════════════════════════════════════════════════
function renderChannels() {
  const grid = $('#channelCards');
  if (!channelData.length) {
    grid.innerHTML = `<div class="empty-state"><p>No channels configured. Edit channels.yaml in Settings.</p></div>`;
    return;
  }
  grid.innerHTML = channelData.map(c => {
    const color = nicheColor(c.niche);
    const topics = (c.recent_topics || []).reverse().slice(0,3);
    return `<div class="ch-card">
      <div class="ch-card-stripe" style="background:linear-gradient(90deg,${color},transparent)"></div>
      <div class="ch-card-body">
        <span class="ch-card-niche" style="color:${color};background:${color}18">${esc(c.niche)}</span>
        <div class="ch-card-name">${esc(c.name)}</div>
        <div class="ch-card-tone">${esc(c.tone || '')}</div>
        <div class="ch-card-stats">
          <div class="ch-stat"><div class="ch-stat-num">${c.produced}</div><div class="ch-stat-lbl">Produced</div></div>
          <div class="ch-stat"><div class="ch-stat-num">${c.posts_per_day}</div><div class="ch-stat-lbl">Per day</div></div>
          <div class="ch-stat"><div class="ch-stat-num">${(c.platforms||[]).length}</div><div class="ch-stat-lbl">Platforms</div></div>
        </div>
        <div class="ch-platforms">${(c.platforms||[]).map(p=>`<span class="plat-tag">${esc(p)}</span>`).join('')}</div>
        ${topics.length ? `<div class="ch-recent">
          <div class="ch-recent-title">Recent topics</div>
          ${topics.map(t=>`<div class="ch-topic">${esc(t)}</div>`).join('')}
        </div>` : ''}
        <div class="ch-actions">
          <button class="btn-primary btn-sm" data-key="${esc(c.key)}">▶ Generate</button>
          <button class="btn-ghost btn-sm" onclick="navigateTo('settings')">Edit</button>
        </div>
      </div>
    </div>`;
  }).join('');
  $$('.ch-card .btn-primary').forEach(btn => {
    btn.addEventListener('click', () => quickGenerate(btn.dataset.key));
  });
}

// ════════════════════════════════════════════════════════
// GUIDE
// ════════════════════════════════════════════════════════
let guideLoaded = false;
async function loadGuide() {
  if (guideLoaded) return;
  try {
    const html = await fetch('guide.html').then(r => r.text());
    $('#guideContent').innerHTML = html;
    guideLoaded = true;
    initGuideFaq();
    initGuideTocHighlight();
  } catch(e) {
    $('#guideContent').innerHTML = `<p style="color:var(--text2);padding:24px">Could not load guide: ${esc(e.message)}</p>`;
  }
}
function initGuideFaq() {
  $$('.faq-item .faq-q').forEach(q => {
    q.addEventListener('click', () => q.parentElement.classList.toggle('open'));
  });
}
function initGuideTocHighlight() {
  const links = $$('.toc-link');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === `#${e.target.id}`));
      }
    });
  }, { rootMargin: '-20% 0px -60% 0px' });
  $$('.g-section[id]').forEach(s => observer.observe(s));
}

// ════════════════════════════════════════════════════════
// SETTINGS
// ════════════════════════════════════════════════════════
let activeCfg = 'settings.yaml';

$$('.stab').forEach(tab => {
  tab.addEventListener('click', () => {
    $$('.stab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    if (tab.dataset.cfg === 'keys') {
      $('#settingsEditor').classList.remove('active');
      $('#settingsEditor').style.display = 'none';
      $('#settingsKeys').style.display = '';
      loadKeyPanel();
    } else {
      $('#settingsEditor').style.display = '';
      $('#settingsKeys').style.display = 'none';
      loadCfgEditor(tab.dataset.cfg);
    }
  });
});

async function loadCfgEditor(name) {
  activeCfg = name;
  try {
    const { content } = await api(`/config/${name}`);
    $('#cfgEditor').value = content;
    $('#cfgMsg').textContent = '';
    $('#cfgMsg').className = 'save-msg';
  } catch(e) { toast('Load failed: ' + e.message, 'error'); }
}

$('#cfgSave').addEventListener('click', async () => {
  try {
    await api(`/config/${activeCfg}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: $('#cfgEditor').value }),
    });
    $('#cfgMsg').textContent = '✓ Saved successfully';
    $('#cfgMsg').className = 'save-msg ok';
    toast('Configuration saved', 'success');
    const ch = await api('/channels').catch(() => []);
    channelData = ch;
    renderQuickChannels();
    renderGenChannelPicker();
    renderChannels();
  } catch(e) {
    $('#cfgMsg').textContent = '✗ ' + e.message;
    $('#cfgMsg').className = 'save-msg err';
    toast('Save failed: ' + e.message, 'error');
  }
});

async function loadKeyPanel() {
  const env = await api('/env-status').catch(() => ({}));
  const KEYS = [
    { key:'ANTHROPIC_API_KEY', label:'Anthropic (Claude)', tag:'LLM' },
    { key:'OPENAI_API_KEY',    label:'OpenAI (GPT)',       tag:'LLM' },
    { key:'ELEVENLABS_API_KEY',label:'ElevenLabs',         tag:'Voice' },
    { key:'PEXELS_API_KEY',    label:'Pexels',             tag:'Visuals' },
    { key:'FAL_KEY',           label:'fal.ai',             tag:'AI Images' },
    { key:'REPLICATE_API_TOKEN',label:'Replicate',         tag:'AI Images' },
    { key:'AYRSHARE_API_KEY',  label:'Ayrshare',           tag:'Publishing' },
    { key:'UPLOAD_POST_API_KEY',label:'upload-post.com',   tag:'Publishing' },
  ];
  $('#keysGrid').innerHTML = KEYS.map(k =>
    `<div class="key-item">
      <div class="key-status-dot ${env[k.key]?'on':'off'}"></div>
      <div class="key-name">${esc(k.label)}</div>
      <span class="key-tag">${esc(k.tag)}</span>
      <span class="key-state ${env[k.key]?'on':'off'}">${env[k.key]?'Configured':'Missing'}</span>
    </div>`).join('');
  loadSidebarKeys(env);
}

// ════════════════════════════════════════════════════════
// VIEW REGISTRY + BOOT
// ════════════════════════════════════════════════════════
VIEWS.dashboard = loadDashboard;
VIEWS.generate  = renderGenChannelPicker;
VIEWS.library   = loadLibraryData;
VIEWS.channels  = renderChannels;
VIEWS.guide     = loadGuide;
VIEWS.settings  = () => loadCfgEditor(activeCfg);

(async () => {
  channelData = await api('/channels').catch(() => []);
  loadDashboard();
  loadLibraryData();
  setInterval(() => {
    if ($('#view-dashboard').classList.contains('active')) loadDashboard();
    if (activeJobId) {/* polling already running */}
  }, 8000);
})();
