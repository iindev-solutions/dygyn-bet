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
const TOTAL_CONFIDENCE_POINTS = 100;

const state = {
  me: null,
  events: [],
  selectedEvent: null,
  selectedPlayer: null,
  players: [],
  disciplines: [],
  draftAllocationsByEvent: {},
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
  if (name === 'admin') loadAdmin();
}

async function loadMe() {
  const data = await api('/api/me');
  state.me = data.user;
  const name = [data.user.first_name, data.user.last_name].filter(Boolean).join(' ') || data.user.username || data.user.telegram_id;
  $('#userLine').textContent = `Вы вошли как ${name}`;
  $('#adminTabBtn').hidden = !data.user.is_admin;
}

async function loadDisciplines() {
  if (state.disciplines.length) return state.disciplines;
  const data = await api('/api/disciplines');
  state.disciplines = data.disciplines;
  return state.disciplines;
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
  state.draftAllocationsByEvent[data.event.id] = allocationsFromPicks(data.event.my_picks || []);
  renderEventsList();
}

function allocationsFromPicks(picks) {
  const out = {};
  for (const pick of picks) out[Number(pick.player_id)] = Number(pick.confidence_points || 0);
  return out;
}

function getDraftAllocations(event = state.selectedEvent) {
  if (!event) return {};
  if (state.draftAllocationsByEvent[event.id]) return state.draftAllocationsByEvent[event.id];
  return allocationsFromPicks(event.my_picks || []);
}

function getDraftPlayerIds(event = state.selectedEvent) {
  return Object.keys(getDraftAllocations(event)).map(Number);
}

function getAllocationTotal(event = state.selectedEvent) {
  return Object.values(getDraftAllocations(event)).reduce((sum, points) => sum + Number(points || 0), 0);
}

function getParticipantById(playerId, event = state.selectedEvent) {
  return event?.participants?.find(p => Number(p.id) === Number(playerId));
}

function getPickedNames(event = state.selectedEvent) {
  if (!event) return [];
  return getDraftPlayerIds(event).map(id => getParticipantById(id, event)?.name).filter(Boolean);
}

function getPickedSummaries(event = state.selectedEvent) {
  const allocations = getDraftAllocations(event);
  return getDraftPlayerIds(event).map(id => `${getParticipantById(id, event)?.name || id} — ${allocations[id]} очков`);
}

function getTotalPoints(event) {
  return Number(event?.totals?.points || 0);
}

function supportPercent(event, participant) {
  const totalPoints = getTotalPoints(event);
  const points = Number(participant.confidence_sum || 0);
  return totalPoints ? Math.round(points / totalPoints * 100) : 0;
}

function topSupport(event, limit = 3) {
  if (!event?.participants?.length) return [];
  return [...event.participants]
    .sort((a, b) => Number(b.confidence_sum || 0) - Number(a.confidence_sum || 0))
    .slice(0, limit);
}

function evenAllocation(playerIds) {
  if (!playerIds.length) return {};
  const base = Math.floor(TOTAL_CONFIDENCE_POINTS / playerIds.length);
  let remainder = TOTAL_CONFIDENCE_POINTS - base * playerIds.length;
  const out = {};
  for (const playerId of playerIds) {
    out[playerId] = base + (remainder > 0 ? 1 : 0);
    remainder -= 1;
  }
  return out;
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
  state.draftAllocationsByEvent[eventId] = evenAllocation(picks);
  renderEventsList();
}

function setDraftAllocation(playerId, points) {
  if (!state.selectedEvent) return;
  const eventId = state.selectedEvent.id;
  const allocations = { ...getDraftAllocations() };
  allocations[playerId] = Math.max(1, Math.min(TOTAL_CONFIDENCE_POINTS, Number(points || 1)));
  state.draftAllocationsByEvent[eventId] = allocations;
  renderEventsList();
}

function rebalanceDraftAllocations() {
  if (!state.selectedEvent) return;
  state.draftAllocationsByEvent[state.selectedEvent.id] = evenAllocation(getDraftPlayerIds());
  renderEventsList();
}

function renderEventsList() {
  const box = $('#eventsList');
  if (!state.events.length) {
    box.innerHTML = '<div class="card empty">Пока нет событий.</div>';
    return;
  }
  const selected = state.selectedEvent;
  const hero = selected ? renderEventHero(selected) : '';
  const eventPicker = state.events.map(e => `
    <button class="choice ${selected?.id === e.id ? 'selected' : ''}" data-event-id="${e.id}">
      <span>${escapeHtml(e.title)}<br><small>${formatDate(e.starts_at)} · ${e.participant_count} участников · ${e.pick_count} голосов</small></span>
      <strong>${statusLabel(e.status)}</strong>
    </button>
  `).join('');

  const detail = selected ? renderEventDetail(selected) : '';
  box.innerHTML = `${hero}<article class="card"><h2>События</h2><div class="choices">${eventPicker}</div></article>${detail}`;
  bindEventScreenActions(box);
}

function bindEventScreenActions(scope) {
  scope.querySelectorAll('[data-event-id]').forEach(btn => btn.addEventListener('click', () => loadEvent(btn.dataset.eventId)));
  scope.querySelectorAll('[data-pick-player]').forEach(btn => btn.addEventListener('click', () => toggleDraftPick(Number(btn.dataset.pickPlayer))));
  scope.querySelectorAll('[data-allocation-player]').forEach(input => input.addEventListener('change', () => {
    setDraftAllocation(Number(input.dataset.allocationPlayer), Number(input.value));
  }));
  $('#rebalanceAllocationsBtn')?.addEventListener('click', rebalanceDraftAllocations);
  $('#savePicksBtn')?.addEventListener('click', sendPicks);
  $('#copyShareBtn')?.addEventListener('click', copyShareText);
  $('#nativeShareBtn')?.addEventListener('click', nativeShare);
  $('#storyCardBtn')?.addEventListener('click', downloadStoryCard);
}

function renderEventHero(event) {
  const leaders = topSupport(event, 3);
  const supportRows = leaders.length ? leaders.map(p => {
    const percent = supportPercent(event, p);
    return `<div class="history-item"><div class="row"><strong>${escapeHtml(p.name)}</strong><span>${percent}%</span></div><div class="progress"><span style="width:${percent}%"></span></div></div>`;
  }).join('') : '<p class="muted">Поддержка появится после первых голосов.</p>';
  return `
    <article class="card event-card">
      <div class="row">
        <span class="badge">${statusLabel(event.status)}</span>
        <span class="badge blue">Игры Дыгына — голосование</span>
      </div>
      <h2 style="margin-top:18px">${escapeHtml(event.title)}</h2>
      <p class="muted">Голосование и поддержка участников</p>
      <div class="stat-grid">
        <div class="stat-box"><strong>${event.participant_count || event.participants?.length || 0}</strong><span>участников</span></div>
        <div class="stat-box"><strong>${event.totals?.picks || 0}</strong><span>голосов</span></div>
        <div class="stat-box"><strong>${formatDate(event.starts_at)}</strong><span>старт</span></div>
      </div>
      <div class="history" style="margin-top:14px"><h3>Сейчас болеют за</h3>${supportRows}</div>
    </article>
  `;
}

function renderEventDetail(event) {
  const draftIds = getDraftPlayerIds(event);
  const draftIdSet = new Set(draftIds);
  const canPick = event.status === 'open';
  const participants = event.participants.map((p, index) => renderParticipantChoice(event, p, index, draftIdSet, canPick)).join('');
  const results = event.results?.length ? `
    <div class="history"><h3>Итоги</h3>${event.results.map(r => `
      <div class="history-item">${r.place} место — ${escapeHtml(r.player_name)} ${r.score ? `· ${r.score}` : ''}</div>
    `).join('')}</div>
  ` : '';
  return `
    <article class="card">
      <div class="row">
        <div>
          <h2>Кто победит?</h2>
          <p class="muted">Выберите до ${MAX_PICKS} участников · ${draftIds.length}/${MAX_PICKS}</p>
        </div>
        <span class="badge">${statusLabel(event.status)}</span>
      </div>
      <div class="support-list">${participants || '<div class="empty">Участники не добавлены.</div>'}</div>
      ${canPick ? renderConfidenceBlock(draftIds) : '<p class="muted">Голосование закрыто.</p>'}
      ${renderShareBlock(event, draftIds)}
      ${results}
      ${renderLiveResults(event.live_results)}
    </article>`;
}

function renderParticipantChoice(event, participant, index, draftIdSet, canPick) {
  const points = Number(participant.confidence_sum || 0);
  const percent = supportPercent(event, participant);
  const selected = draftIdSet.has(Number(participant.id));
  const allocation = getDraftAllocations(event)[Number(participant.id)];
  return `
    <button class="participant-card ${selected ? 'selected' : ''}" data-pick-player="${participant.id}" ${canPick ? '' : 'disabled'}>
      <span>
        <strong><span class="rank-dot">${index + 1}</span>${escapeHtml(participant.name)}</strong><br>
        <small>${escapeHtml(participant.region || 'регион не указан')} · ${participant.pick_count} голосов · ${points} очков${selected ? ` · мой голос ${allocation}` : ''}</small>
        <span class="progress"><span style="width:${percent}%"></span></span>
      </span>
      <span class="percent">${selected ? `${allocation}` : `${percent}%`}</span>
    </button>
  `;
}

function renderConfidenceBlock(draftIds) {
  const allocations = getDraftAllocations();
  const total = getAllocationTotal();
  const isValid = draftIds.length > 0 && total === TOTAL_CONFIDENCE_POINTS;
  const rows = draftIds.map(playerId => {
    const participant = getParticipantById(playerId);
    const value = allocations[playerId] || 1;
    return `
      <div class="allocation-row">
        <div class="row"><strong>${escapeHtml(participant?.name || playerId)}</strong><span>${value}</span></div>
        <input type="range" min="1" max="100" value="${value}" data-allocation-player="${playerId}" />
      </div>
    `;
  }).join('') || '<p class="muted">Выберите участника — ему автоматически достанутся 100 очков.</p>';
  return `
    <div class="confidence">
      <div class="row"><strong>Распределите 100 очков</strong><span class="allocation-total ${isValid ? 'valid' : 'invalid'}">${total}/${TOTAL_CONFIDENCE_POINTS}</span></div>
      <p class="muted">Можно выбрать 1–3 участников. Сумма должна быть ровно 100.</p>
      <div class="allocation-list">${rows}</div>
      ${draftIds.length > 1 ? '<button id="rebalanceAllocationsBtn" class="ghost wide" type="button">Распределить поровну</button>' : ''}
      <div class="bottom-bar">
        <button id="savePicksBtn" class="primary wide" ${isValid ? '' : 'disabled'}>Сохранить голос</button>
      </div>
    </div>
  `;
}

function renderLiveResults(results) {
  if (!results) return '';
  const standings = results.standings || [];
  const disciplineRows = results.discipline_results || [];
  if (!standings.length && !disciplineRows.length) return '';
  const standingsHtml = [0, 1, 2].map(day => {
    const rows = standings.filter(row => Number(row.day_number) === day).slice(0, 5);
    if (!rows.length) return '';
    const title = day === 0 ? 'Общий зачёт' : `День ${day}`;
    return `<div class="history-item"><strong>${title}</strong>${rows.map(row => `<div class="row"><span>${row.place}. ${escapeHtml(row.player_name)}</span><span>${row.total_points ?? '—'}${row.is_winner ? ' · победитель' : ''}</span></div>`).join('')}</div>`;
  }).join('');
  const dayRows = [1, 2].map(day => {
    const rows = disciplineRows.filter(row => Number(row.day_number) === day).slice(0, 8);
    if (!rows.length) return '';
    return `<div class="history-item"><strong>Результаты: день ${day}</strong>${rows.map(row => `<div class="row"><span>${escapeHtml(row.discipline_name)} · ${escapeHtml(row.player_name)}</span><span>${escapeHtml(row.result_text || row.place || '—')}</span></div>`).join('')}</div>`;
  }).join('');
  return `<div class="history"><h3>Ход Игр</h3>${standingsHtml}${dayRows}<p class="muted">${results.last_updated_at ? `Обновлено: ${formatDate(results.last_updated_at)}` : ''}</p></div>`;
}

function renderShareBlock(event, draftIds) {
  if (!draftIds.length) return '';
  const names = getPickedSummaries(event).map(escapeHtml).join(', ');
  return `
    <div class="share-card">
      <h3>Поделиться выбором</h3>
      <p class="muted">Скачайте карточку и загрузите её в Instagram Stories вручную.</p>
      <p><strong>Мой выбор:</strong> ${names}</p>
      <div class="share-actions">
        <button id="nativeShareBtn" class="ghost">Поделиться</button>
        <button id="copyShareBtn" class="ghost">Скопировать</button>
        <button id="storyCardBtn" class="primary">Карточка</button>
      </div>
    </div>
  `;
}

async function sendPicks() {
  if (!state.selectedEvent) return;
  const allocations = getDraftAllocations();
  const playerIds = getDraftPlayerIds();
  if (!playerIds.length) {
    toast('Выберите хотя бы одного участника');
    return;
  }
  if (getAllocationTotal() !== TOTAL_CONFIDENCE_POINTS) {
    toast('Нужно распределить ровно 100 очков');
    return;
  }
  const data = await api(`/api/events/${state.selectedEvent.id}/prediction`, {
    method: 'POST',
    body: JSON.stringify({
      items: playerIds.map(playerId => ({ participant_id: playerId, confidence_points: allocations[playerId] })),
    })
  });
  state.selectedEvent = data.event;
  state.draftAllocationsByEvent[data.event.id] = allocationsFromPicks(data.event.my_picks || []);
  toast('Голос сохранён');
  await loadEvents();
}

function buildShareText() {
  const names = getPickedSummaries(state.selectedEvent);
  return `Мой голос на Игры Дыгына: ${names.join(', ')}. Голосуй тоже: ${publicAppUrl()}`;
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
      await navigator.share({ title: 'Голосование Игр Дыгына', text, url: publicAppUrl() });
      return;
    } catch (e) {
      if (e.name === 'AbortError') return;
    }
  }
  await copyShareText();
}

function downloadStoryCard() {
  const event = state.selectedEvent;
  const names = getPickedSummaries(event);
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1920;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, '#f2b84b');
  gradient.addColorStop(.38, '#1f2430');
  gradient.addColorStop(1, '#0f1115');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = 'rgba(255,255,255,.12)';
  ctx.beginPath();
  ctx.arc(900, 220, 260, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(120, 1620, 320, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = '900 78px Arial';
  wrapCanvasText(ctx, 'Игры Дыгына — голосование', 90, 220, 900, 92);
  ctx.font = '700 44px Arial';
  wrapCanvasText(ctx, event?.title || 'Голосование', 90, 460, 900, 56);

  ctx.font = '900 54px Arial';
  ctx.fillText('Мой голос:', 90, 720);
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
  const support = state.selectedEvent ? renderSupportStats(state.selectedEvent) : '';
  const leaders = list.length ? list.map((u, i) => {
    const name = [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.telegram_id;
    return `
      <article class="leader-row">
        <span class="avatar">${i + 1}</span>
        <div><strong>${escapeHtml(String(name))}</strong><p class="muted">${u.picks} голосов · ${u.correct || 0} верных</p></div>
        <span class="badge">${u.score} очков</span>
      </article>`;
  }).join('') : '<div class="card empty">Рейтинг появится после первых голосов.</div>';
  $('#leaderboard').innerHTML = `${support}<article class="card"><h2>Рейтинг болельщиков</h2><div class="history">${leaders}</div></article>`;
}

function renderSupportStats(event) {
  const rows = topSupport(event, 10).map((p, index) => {
    const percent = supportPercent(event, p);
    return `
      <div class="history-item">
        <div class="row"><strong>${index + 1}. ${escapeHtml(p.name)}</strong><span class="percent">${percent}%</span></div>
        <p class="muted">${p.pick_count} голосов · ${Number(p.confidence_sum || 0)} очков уверенности</p>
        <div class="progress"><span style="width:${percent}%"></span></div>
      </div>`;
  }).join('') || '<p class="muted">Статистика появится после первых голосов.</p>';
  return `<article class="card"><h2>Статистика поддержки</h2><div class="history">${rows}</div></article>`;
}

async function loadPlayers() {
  const data = await api('/api/players');
  state.players = data.players;
  state.selectedPlayer = null;
  renderPlayersList();
}

async function loadPlayer(playerId) {
  const data = await api(`/api/players/${playerId}`);
  state.selectedPlayer = data.player;
  renderPlayerDetail(data.player);
}

function renderPlayersList() {
  $('#playersList').innerHTML = state.players.map(p => `
    <article class="card player-card">
      <div class="row">
        <div>
          <h2>${escapeHtml(p.name)}</h2>
          <p class="muted">${escapeHtml(p.region || 'регион не указан')}</p>
        </div>
        ${p.avatar_url ? `<img class="player-photo" src="${escapeHtml(p.avatar_url)}" alt="${escapeHtml(p.name)}" loading="lazy">` : `<span class="avatar">${escapeHtml(initials(p.name))}</span>`}
      </div>
      <p>${escapeHtml(p.short_description || p.bio || '')}</p>
      <div class="stat-grid">
        <div class="stat-box"><strong>${p.summary?.wins || 0}</strong><span>побед</span></div>
        <div class="stat-box"><strong>${p.summary?.podiums || 0}</strong><span>топ-3</span></div>
        <div class="stat-box"><strong>${p.summary?.discipline_results_count || 0}</strong><span>результатов</span></div>
      </div>
      <button class="ghost wide details-btn" data-player-id="${p.id}">Открыть статистику</button>
    </article>
  `).join('') || '<div class="card empty">Участники пока не загружены.</div>';
  $('#playersList').querySelectorAll('[data-player-id]').forEach(btn => {
    btn.addEventListener('click', () => loadPlayer(btn.dataset.playerId));
  });
}

function renderPlayerDetail(player) {
  const groups = groupDisciplineResults(player.discipline_results || []);
  const tables = groups.map(group => renderDisciplineTable(group.title, group.rows)).join('') || '<p class="muted">Статистика по видам пока не загружена.</p>';
  $('#playersList').innerHTML = `
    <article class="card player-detail">
      <button class="ghost" id="backToPlayersBtn">← Участники</button>
      <div class="profile-head">
        ${player.avatar_url ? `<img class="profile-photo" src="${escapeHtml(player.avatar_url)}" alt="${escapeHtml(player.name)}" loading="lazy">` : `<span class="profile-photo avatar">${escapeHtml(initials(player.name))}</span>`}
        <div>
          <h2>${escapeHtml(player.name)}</h2>
          <p class="muted">${escapeHtml(player.region || 'регион не указан')}</p>
          ${player.city_or_village ? `<p class="muted">${escapeHtml(player.city_or_village)}</p>` : ''}
        </div>
      </div>
      <p>${escapeHtml(player.short_description || player.bio || '')}</p>
      ${player.strengths ? `<div class="history-item"><strong>Сильные стороны</strong><br><span class="muted">${escapeHtml(player.strengths)}</span></div>` : ''}
      ${player.previous_dygyn_note ? `<div class="history-item"><strong>Опыт Игр Дыгына</strong><br><span class="muted">${escapeHtml(player.previous_dygyn_note)}</span></div>` : ''}
      <div class="stat-grid">
        <div class="stat-box"><strong>${player.summary?.wins || 0}</strong><span>побед</span></div>
        <div class="stat-box"><strong>${player.summary?.podiums || 0}</strong><span>топ-3</span></div>
        <div class="stat-box"><strong>${player.summary?.discipline_events_count || 0}</strong><span>турниров</span></div>
      </div>
    </article>
    ${tables}
  `;
  $('#backToPlayersBtn').addEventListener('click', renderPlayersList);
}

function groupDisciplineResults(results) {
  const map = new Map();
  for (const row of results) {
    const key = `${row.year} · ${row.event_title}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return [...map.entries()].map(([title, rows]) => ({ title, rows }));
}

function renderDisciplineTable(title, rows) {
  const body = rows.map(r => `
    <tr>
      <td><strong>${escapeHtml(r.discipline_name || r.discipline_id)}</strong><br><small>${escapeHtml(r.name_yakut || '')}</small></td>
      <td>${escapeHtml(formatResultValue(r))}</td>
      <td>${r.place ? `${r.place}` : '—'}</td>
      <td>${r.points ?? '—'}</td>
    </tr>
  `).join('');
  return `
    <article class="card">
      <h2>${escapeHtml(title)}</h2>
      <div class="table-wrap">
        <table class="result-table">
          <thead><tr><th>Вид</th><th>Результат</th><th>Место</th><th>Очки</th></tr></thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    </article>
  `;
}

function formatResultValue(row) {
  if (row.result_text) return row.result_text;
  if (row.result_value !== null && row.result_value !== undefined) return `${row.result_value} ${row.result_unit || ''}`.trim();
  return '—';
}

function initials(name) {
  return String(name || '?').split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase();
}

async function loadAdmin() {
  const panel = $('#adminPanel');
  if (!state.me?.is_admin) {
    panel.innerHTML = '<div class="card empty">Нужны права администратора.</div>';
    return;
  }
  await loadDisciplines();
  if (!state.selectedEvent) await loadEvents();
  renderAdminPanel();
}

function renderAdminPanel() {
  const panel = $('#adminPanel');
  const event = state.selectedEvent;
  if (!event) {
    panel.innerHTML = '<div class="card empty">Сначала создайте событие.</div>';
    return;
  }
  const participantOptions = (event.participants || []).map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
  const disciplineOptions = state.disciplines.map(d => `<option value="${escapeHtml(d.discipline_id)}">${escapeHtml(d.name_ru)}</option>`).join('');
  panel.innerHTML = `
    <article class="card">
      <div class="row">
        <div>
          <h2>Админ</h2>
          <p class="muted">${escapeHtml(event.title)} · Day 1 / Day 2 / финал</p>
        </div>
        <button class="ghost" id="adminRefreshBtn">Обновить</button>
      </div>
    </article>

    <article class="card">
      <h2>Результат дисциплины</h2>
      <form id="adminDisciplineForm" class="admin-form">
        <div class="form-grid">
          <label>День<select name="day_number"><option value="1">День 1</option><option value="2">День 2</option></select></label>
          <label>Статус<select name="status"><option value="provisional">Промежуточно</option><option value="official">Официально</option></select></label>
        </div>
        <label>Участник<select name="participant_id">${participantOptions}</select></label>
        <label>Вид<select name="discipline_id">${disciplineOptions}</select></label>
        <div class="form-grid">
          <label>Результат<input name="result_text" placeholder="5:40 / 50 / >102" /></label>
          <label>Число для сортировки<input name="result_value" type="number" step="0.01" placeholder="340" /></label>
        </div>
        <div class="form-grid">
          <label>Единица<input name="result_unit" placeholder="секунды / метры / очки" /></label>
          <label>Место<input name="place" type="number" min="1" /></label>
        </div>
        <label>Очки<input name="points" type="number" step="0.01" /></label>
        <label>Заметка<textarea name="notes" placeholder="Источник / комментарий"></textarea></label>
        <button class="primary wide" type="submit">Сохранить результат</button>
      </form>
    </article>

    <article class="card">
      <h2>Таблица итогов</h2>
      <form id="adminStandingForm" class="admin-form">
        <div class="form-grid">
          <label>Раздел<select name="day_number"><option value="1">День 1</option><option value="2">День 2</option><option value="0">Общий зачёт</option></select></label>
          <label>Статус<select name="status"><option value="provisional">Промежуточно</option><option value="official">Официально</option></select></label>
        </div>
        <label>Участник<select name="participant_id">${participantOptions}</select></label>
        <div class="form-grid">
          <label>Место<input name="place" type="number" min="1" required /></label>
          <label>Сумма очков<input name="total_points" type="number" step="0.01" /></label>
        </div>
        <label><span><input name="is_winner" type="checkbox" /> Победитель</span></label>
        <label>Заметка<textarea name="notes" placeholder="Источник / комментарий"></textarea></label>
        <button class="primary wide" type="submit">Сохранить строку</button>
      </form>
    </article>

    <article class="card">
      <h2>Завершить событие</h2>
      <form id="adminFinishForm" class="admin-form">
        <label>Победитель<select name="winner_participant_id">${participantOptions}</select></label>
        <button class="primary wide" type="submit">Зафиксировать победителя и начислить очки</button>
      </form>
    </article>

    <article class="card">
      <h2>Текущие результаты</h2>
      ${renderLiveResults(event.live_results) || '<p class="muted">Результаты ещё не внесены.</p>'}
    </article>
  `;
  bindAdminPanel(event);
}

function bindAdminPanel(event) {
  $('#adminRefreshBtn')?.addEventListener('click', async () => {
    await loadEvent(event.id);
    await loadAdmin();
    toast('Админка обновлена');
  });
  $('#adminDisciplineForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await api(`/api/admin/events/${event.id}/discipline-results`, {
      method: 'POST',
      body: JSON.stringify({
        day_number: Number(form.get('day_number')),
        participant_id: Number(form.get('participant_id')),
        discipline_id: String(form.get('discipline_id')),
        result_text: String(form.get('result_text') || ''),
        result_value: numberOrNull(form.get('result_value')),
        result_unit: String(form.get('result_unit') || ''),
        place: numberOrNull(form.get('place')),
        points: numberOrNull(form.get('points')),
        status: String(form.get('status') || 'provisional'),
        notes: String(form.get('notes') || ''),
      })
    });
    await loadEvent(event.id);
    renderAdminPanel();
    toast('Результат сохранён');
  });
  $('#adminStandingForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await api(`/api/admin/events/${event.id}/standings`, {
      method: 'POST',
      body: JSON.stringify({
        day_number: Number(form.get('day_number')),
        participant_id: Number(form.get('participant_id')),
        place: Number(form.get('place')),
        total_points: numberOrNull(form.get('total_points')),
        is_winner: form.get('is_winner') === 'on',
        status: String(form.get('status') || 'provisional'),
        notes: String(form.get('notes') || ''),
      })
    });
    await loadEvent(event.id);
    renderAdminPanel();
    toast('Таблица сохранена');
  });
  $('#adminFinishForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    if (!confirm('Завершить событие и начислить очки болельщикам?')) return;
    const data = await api(`/api/admin/events/${event.id}/finish`, {
      method: 'POST',
      body: JSON.stringify({ winner_participant_id: Number(form.get('winner_participant_id')) })
    });
    state.selectedEvent = data.event;
    await loadEvents();
    await loadAdmin();
    toast('Событие завершено');
  });
}

function numberOrNull(value) {
  const text = String(value ?? '').trim();
  return text ? Number(text) : null;
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
