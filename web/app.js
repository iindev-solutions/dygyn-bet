const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const scriptPath = new URL(document.currentScript.src).pathname;
const appBasePath = scriptPath.replace(/\/static\/app\.js$/, '');
const appUrl = (path) => `${appBasePath}${path}`;
const publicAppUrl = () => `${window.location.origin}${appBasePath || ''}/`;

const MAX_PICKS = 3;

const state = {
  me: null,
  events: [],
  selectedEvent: null,
  players: [],
  confidence: 25,
  draftPicksByEvent: {},
};

const $ = (sel) => document.querySelector(sel);

function toast(message) {
  const el = $('#toast');
  el.textContent = message;
  el.hidden = false;
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { el.hidden = true; }, 2600);
  tg?.HapticFeedback?.notificationOccurred?.('success');
}

async function api(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (tg?.initData) headers['X-Telegram-Init-Data'] = tg.initData;
  const res = await fetch(appUrl(path), { ...options, headers });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.detail || 'Ошибка запроса');
  return json;
}

function formatDate(iso) {
  try {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

function statusLabel(status) {
  return {
    draft: 'черновик', open: 'открыто', locked: 'закрыто', settled: 'итоги'
  }[status] || status;
}

function switchTab(name) {
  document.querySelectorAll('.tabs button').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab').forEach(s => s.classList.toggle('active', s.id === name));
  if (name === 'stats') loadLeaderboard();
  if (name === 'players') loadPlayers();
}

async function loadMe() {
  const data = await api('/api/me');
  state.me = data.user;
  const name = [data.user.first_name, data.user.last_name].filter(Boolean).join(' ') || data.user.username || data.user.telegram_id;
  $('#userLine').textContent = `Вы вошли как ${name}`;
}

async function loadEvents() {
  const data = await api('/api/events');
  state.events = data.events;
  const selectedId = state.selectedEvent?.id;
  const nextEvent = state.events.find(e => Number(e.id) === Number(selectedId)) || state.events.find(e => e.status === 'open') || state.events[0];
  if (nextEvent) await loadEvent(nextEvent.id);
  renderEventsList();
}

async function loadEvent(id) {
  const data = await api(`/api/events/${id}`);
  state.selectedEvent = data.event;
  state.draftPicksByEvent[data.event.id] = (data.event.my_picks || []).map(p => Number(p.player_id));
  renderEventsList();
}

function getDraftPlayerIds(event = state.selectedEvent) {
  if (!event) return [];
  if (state.draftPicksByEvent[event.id]) return state.draftPicksByEvent[event.id];
  return (event.my_picks || []).map(p => Number(p.player_id));
}

function getPickedNames(event = state.selectedEvent) {
  if (!event) return [];
  const ids = new Set(getDraftPlayerIds(event));
  return event.participants.filter(p => ids.has(Number(p.id))).map(p => p.name);
}

function toggleDraftPick(playerId) {
  if (!state.selectedEvent) return;
  const eventId = state.selectedEvent.id;
  const picks = [...getDraftPlayerIds()];
  const index = picks.indexOf(playerId);
  if (index >= 0) {
    picks.splice(index, 1);
  } else {
    if (picks.length >= MAX_PICKS) {
      toast(`Можно выбрать максимум ${MAX_PICKS} участников`);
      return;
    }
    picks.push(playerId);
  }
  state.draftPicksByEvent[eventId] = picks;
  renderEventsList();
}

function renderEventsList() {
  const box = $('#eventsList');
  if (!state.events.length) {
    box.innerHTML = '<div class="card empty">Пока нет событий.</div>';
    return;
  }
  const selected = state.selectedEvent;
  const eventPicker = state.events.map(e => `
    <button class="choice ${selected?.id === e.id ? 'selected' : ''}" data-event-id="${e.id}">
      <span>${escapeHtml(e.title)}<br><small>${formatDate(e.starts_at)} · ${e.participant_count} участников · ${e.pick_count} голосов</small></span>
      <strong>${statusLabel(e.status)}</strong>
    </button>
  `).join('');

  const detail = selected ? renderEventDetail(selected) : '';
  box.innerHTML = `<article class="card"><h2>Выберите событие</h2><div class="choices">${eventPicker}</div></article>${detail}`;
  box.querySelectorAll('[data-event-id]').forEach(btn => btn.addEventListener('click', () => loadEvent(btn.dataset.eventId)));
  box.querySelectorAll('[data-pick-player]').forEach(btn => btn.addEventListener('click', () => toggleDraftPick(Number(btn.dataset.pickPlayer))));
  $('#savePicksBtn')?.addEventListener('click', sendPicks);
  $('#copyShareBtn')?.addEventListener('click', copyShareText);
  $('#nativeShareBtn')?.addEventListener('click', nativeShare);
  $('#storyCardBtn')?.addEventListener('click', downloadStoryCard);
  const slider = $('#confidenceRange');
  if (slider) {
    slider.value = String(state.confidence);
    slider.addEventListener('input', () => {
      state.confidence = Number(slider.value);
      $('#confidenceValue').textContent = state.confidence;
    });
  }
}

function renderEventDetail(event) {
  const totalPoints = Number(event.totals.points || 0);
  const draftIds = getDraftPlayerIds(event);
  const draftIdSet = new Set(draftIds);
  const canPick = event.status === 'open';
  const participants = event.participants.map(p => {
    const points = Number(p.confidence_sum || 0);
    const percent = totalPoints ? Math.round(points / totalPoints * 100) : 0;
    const selected = draftIdSet.has(Number(p.id));
    return `
      <button class="choice ${selected ? 'selected' : ''}" data-pick-player="${p.id}" ${canPick ? '' : 'disabled'}>
        <span>${escapeHtml(p.name)}<br><small>${escapeHtml(p.region || 'регион не указан')} · ${p.pick_count} голосов · ${points} очков${selected ? ' · выбран' : ''}</small>
          <span class="meter"><span style="width:${percent}%"></span></span>
        </span>
        <strong>${selected ? '✓' : `${percent}%`}</strong>
      </button>
    `;
  }).join('');
  const results = event.results?.length ? `
    <div class="history"><h3>Итоги</h3>${event.results.map(r => `
      <div class="history-item">${r.place} место — ${escapeHtml(r.player_name)} ${r.score ? `· ${r.score}` : ''}</div>
    `).join('')}</div>
  ` : '';
  return `
    <article class="card">
      <div class="row">
        <div>
          <h2>${escapeHtml(event.title)}</h2>
          <p class="muted">${escapeHtml(event.description || '')}</p>
        </div>
        <span class="badge">${statusLabel(event.status)}</span>
      </div>
      <p class="muted">Старт: ${formatDate(event.starts_at)} · всего голосов: ${event.totals.picks || 0}</p>
      <p><strong>Выберите до ${MAX_PICKS} участников</strong> <span class="muted">(${draftIds.length}/${MAX_PICKS})</span></p>
      <div class="choices">${participants || '<div class="empty">Участники не добавлены.</div>'}</div>
      ${canPick ? `
        <div class="confidence">
          <div class="row"><strong>Очки уверенности каждому выбранному</strong><span id="confidenceValue">${state.confidence}</span></div>
          <input id="confidenceRange" type="range" min="1" max="100" value="${state.confidence}" />
          <button id="savePicksBtn" class="primary wide" ${draftIds.length ? '' : 'disabled'}>Сохранить голос</button>
        </div>
      ` : '<p class="muted">Прогнозы закрыты.</p>'}
      ${renderShareBlock(event, draftIds)}
      ${results}
    </article>`;
}

function renderShareBlock(event, draftIds) {
  if (!draftIds.length) return '';
  const names = getPickedNames(event).map(escapeHtml).join(', ');
  return `
    <div class="share-card">
      <h3>Раскрутить голосование</h3>
      <p class="muted">Поделитесь своим выбором. Для Instagram Stories скачайте карточку и загрузите её в сторис вручную.</p>
      <p><strong>Мой выбор:</strong> ${names}</p>
      <div class="share-actions">
        <button id="nativeShareBtn" class="ghost">Поделиться</button>
        <button id="copyShareBtn" class="ghost">Скопировать текст</button>
        <button id="storyCardBtn" class="primary">Карточка для сторис</button>
      </div>
    </div>
  `;
}

async function sendPicks() {
  if (!state.selectedEvent) return;
  const playerIds = getDraftPlayerIds();
  if (!playerIds.length) {
    toast('Выберите хотя бы одного участника');
    return;
  }
  const data = await api('/api/picks', {
    method: 'POST',
    body: JSON.stringify({
      event_id: state.selectedEvent.id,
      player_ids: playerIds,
      confidence_points: state.confidence,
    })
  });
  state.selectedEvent = data.event;
  state.draftPicksByEvent[data.event.id] = (data.event.my_picks || []).map(p => Number(p.player_id));
  toast('Голос сохранён');
  await loadEvents();
}

function buildShareText() {
  const event = state.selectedEvent;
  const names = getPickedNames(event);
  const url = publicAppUrl();
  return `Я выбрал участников Игр Дыгына: ${names.join(', ')}. Голосуй тоже: ${url}`;
}

async function copyShareText() {
  const text = buildShareText();
  try {
    await navigator.clipboard.writeText(text);
    toast('Текст скопирован');
  } catch {
    window.prompt('Скопируйте текст:', text);
  }
}

async function nativeShare() {
  const text = buildShareText();
  if (navigator.share) {
    try {
      await navigator.share({ title: 'Фан-прогнозы Игр Дыгына', text, url: publicAppUrl() });
      return;
    } catch (e) {
      if (e.name === 'AbortError') return;
    }
  }
  await copyShareText();
}

function downloadStoryCard() {
  const event = state.selectedEvent;
  const names = getPickedNames(event);
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1920;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, '#2563eb');
  gradient.addColorStop(1, '#111827');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = 'rgba(255,255,255,.14)';
  ctx.beginPath();
  ctx.arc(900, 220, 260, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(120, 1620, 320, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = '900 78px Arial';
  wrapCanvasText(ctx, 'Фан-прогнозы Игр Дыгына', 90, 220, 900, 92);
  ctx.font = '700 44px Arial';
  wrapCanvasText(ctx, event?.title || 'Голосование', 90, 460, 900, 56);

  ctx.font = '900 54px Arial';
  ctx.fillText('Мой выбор:', 90, 720);
  ctx.font = '800 64px Arial';
  names.forEach((name, index) => {
    wrapCanvasText(ctx, `${index + 1}. ${name}`, 120, 830 + index * 170, 840, 72);
  });

  ctx.font = '700 42px Arial';
  wrapCanvasText(ctx, 'Голосуй тоже в Telegram Mini App', 90, 1510, 900, 56);
  ctx.font = '600 34px Arial';
  wrapCanvasText(ctx, publicAppUrl(), 90, 1640, 900, 46);

  const link = document.createElement('a');
  link.download = 'dygyn-story-card.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
  toast('Карточка готова для сторис');
}

function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = String(text).split(' ');
  let line = '';
  for (const word of words) {
    const testLine = line ? `${line} ${word}` : word;
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, y);
      line = word;
      y += lineHeight;
    } else {
      line = testLine;
    }
  }
  if (line) ctx.fillText(line, x, y);
}

async function loadLeaderboard() {
  const data = await api('/api/leaderboard');
  const list = data.leaderboard;
  $('#leaderboard').innerHTML = list.length ? list.map((u, i) => {
    const name = [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.telegram_id;
    return `<article class="card row"><div><strong>${i + 1}. ${escapeHtml(String(name))}</strong><p class="muted">${u.picks} голосов · ${u.correct || 0} верных</p></div><span class="badge">${u.score} очков</span></article>`;
  }).join('') : '<div class="card empty">Рейтинг появится после первых голосов.</div>';
}

async function loadPlayers() {
  const data = await api('/api/players');
  state.players = data.players;
  $('#playersList').innerHTML = state.players.map(p => `
    <article class="card">
      <div class="row"><div><h2>${escapeHtml(p.name)}</h2><p class="muted">${escapeHtml(p.region || '')}</p></div><span class="badge">${p.summary?.wins || 0} побед</span></div>
      <p>${escapeHtml(p.bio || '')}</p>
      <div class="history">
        ${(p.history || []).map(h => `<div class="history-item"><strong>${h.year} · ${escapeHtml(h.competition)}</strong><br><span class="muted">${h.place ? `${h.place} место` : 'место не указано'}${h.score ? ` · ${h.score} очков` : ''}</span><br>${escapeHtml(h.notes || '')}</div>`).join('') || '<p class="muted">История пока не добавлена.</p>'}
      </div>
    </article>
  `).join('');
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
  }[ch]));
}

async function boot() {
  document.querySelectorAll('.tabs button').forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
  $('#refreshBtn').addEventListener('click', async () => {
    await loadEvents();
    toast('Обновлено');
  });
  try {
    await loadMe();
    await loadEvents();
    if (location.hash === '#stats') switchTab('stats');
  } catch (e) {
    $('#eventsList').innerHTML = `<div class="card"><h2>Не удалось открыть сервис</h2><p class="muted">${escapeHtml(e.message)}</p><p>Откройте приложение из Telegram-кнопки бота или включите ALLOW_DEV_LOGIN=1 для локальной разработки.</p></div>`;
  }
}

boot();
