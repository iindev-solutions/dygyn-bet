const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const state = {
  me: null,
  events: [],
  selectedEvent: null,
  players: [],
  confidence: 25,
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
  const res = await fetch(path, { ...options, headers });
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
  const firstOpen = state.events.find(e => e.status === 'open') || state.events[0];
  if (firstOpen) await loadEvent(firstOpen.id);
  renderEventsList();
}

async function loadEvent(id) {
  const data = await api(`/api/events/${id}`);
  state.selectedEvent = data.event;
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
      <span>${escapeHtml(e.title)}<br><small>${formatDate(e.starts_at)} · ${e.participant_count} участников</small></span>
      <strong>${statusLabel(e.status)}</strong>
    </button>
  `).join('');

  const detail = selected ? renderEventDetail(selected) : '';
  box.innerHTML = `<article class="card"><h2>Выберите событие</h2><div class="choices">${eventPicker}</div></article>${detail}`;
  box.querySelectorAll('[data-event-id]').forEach(btn => btn.addEventListener('click', () => loadEvent(btn.dataset.eventId)));
  box.querySelectorAll('[data-pick-player]').forEach(btn => btn.addEventListener('click', () => sendPick(Number(btn.dataset.pickPlayer))));
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
  const myPlayerId = event.my_pick?.player_id;
  const canPick = event.status === 'open';
  const participants = event.participants.map(p => {
    const points = Number(p.confidence_sum || 0);
    const percent = totalPoints ? Math.round(points / totalPoints * 100) : 0;
    const selected = Number(myPlayerId) === Number(p.id);
    return `
      <button class="choice ${selected ? 'selected' : ''}" data-pick-player="${p.id}" ${canPick ? '' : 'disabled'}>
        <span>${escapeHtml(p.name)}<br><small>${escapeHtml(p.region || 'регион не указан')} · ${p.pick_count} голосов · ${points} очков</small>
          <span class="meter"><span style="width:${percent}%"></span></span>
        </span>
        <strong>${percent}%</strong>
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
      <p class="muted">Старт: ${formatDate(event.starts_at)} · всего прогнозов: ${event.totals.picks || 0}</p>
      <div class="choices">${participants || '<div class="empty">Участники не добавлены.</div>'}</div>
      ${canPick ? `
        <div class="confidence">
          <div class="row"><strong>Очки уверенности</strong><span id="confidenceValue">${state.confidence}</span></div>
          <input id="confidenceRange" type="range" min="1" max="100" value="${state.confidence}" />
        </div>
      ` : '<p class="muted">Прогнозы закрыты.</p>'}
      ${results}
    </article>`;
}

async function sendPick(playerId) {
  if (!state.selectedEvent) return;
  const data = await api('/api/picks', {
    method: 'POST',
    body: JSON.stringify({
      event_id: state.selectedEvent.id,
      player_id: playerId,
      confidence_points: state.confidence,
    })
  });
  state.selectedEvent = data.event;
  toast('Прогноз сохранён');
  await loadEvents();
}

async function loadLeaderboard() {
  const data = await api('/api/leaderboard');
  const list = data.leaderboard;
  $('#leaderboard').innerHTML = list.length ? list.map((u, i) => {
    const name = [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.telegram_id;
    return `<article class="card row"><div><strong>${i + 1}. ${escapeHtml(String(name))}</strong><p class="muted">${u.picks} прогнозов · ${u.correct || 0} верных</p></div><span class="badge">${u.score} очков</span></article>`;
  }).join('') : '<div class="card empty">Рейтинг появится после первых прогнозов.</div>';
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
    $('#eventsList').innerHTML = `<div class="card"><h2>Не удалось открыть MVP</h2><p class="muted">${escapeHtml(e.message)}</p><p>Откройте приложение из Telegram-кнопки бота или включите ALLOW_DEV_LOGIN=1 для локальной разработки.</p></div>`;
  }
}

boot();
