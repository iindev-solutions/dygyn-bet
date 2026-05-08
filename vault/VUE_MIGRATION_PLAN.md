# Vue 3 Migration Plan — dygyn-bet

Status: implemented on branch `vue-tma-cutover` on 2026-05-07; real mobile Telegram QA and VPS deploy still pending.

Goal: migrate the Telegram Mini App frontend from vanilla JS (`web/`) to Vue 3 without breaking production voting, Telegram auth, story sharing, admin tools, or the A1 ceremonial visual direction.

## Non-Negotiables

- Keep `web/` as the production baseline until the Vue app reaches parity.
- No big-bang cutover: build, test, and preview Vue in parallel first.
- Keep the existing backend API contract and SQLite schema stable unless a frontend parity bug proves otherwise.
- Keep Telegram Mini App auth unchanged: send raw `window.Telegram.WebApp.initData` as `X-Telegram-Init-Data`.
- Keep URL-prefix safety for `https://iindiinda.duckdns.org/dygyn-bet/`; do not take over root `/` or existing `/api`.
- Keep A1 design direction from root `DESIGN.md`; port CSS 1:1 before refactoring styles.
- Keep the product legal boundary: votes/confidence points only; no money, odds, payouts, deposits, withdrawals, or value prizes.
- Migrate admin last and test admin writes only on a non-production DB first.
- Keep rollback simple: no DB migration required for the frontend rewrite.

## Current Frontend Contract

- `web/index.html` is the TMA shell.
- `web/app.js` owns Telegram init, API wrapper, state, rendering, voting, player detail, story card, admin forms, and toast.
- `web/styles.css` owns the current dark/card/gold A1 look.
- FastAPI currently serves:
  - `/` → `web/index.html` with `Cache-Control: no-store`;
  - `/static/*` → files from `web/`;
  - `/api/*` → JSON API.
- Nginx currently proxies `/dygyn-bet/` to FastAPI and strips the prefix. Browser requests still include the prefix.
- Existing JS derives its app base from `static/app.js`; Vue must keep equivalent prefix-safe behavior.

## Architecture Decisions

### Core Stack

- Vue 3 with Composition API and `<script setup>`.
- TypeScript with `strict: true`.
- Vite.
- Vue Router.
- Pinia for shared domain state.
- Native `fetch` wrapper instead of Axios by default. Reason: smaller bundle, no interceptor typing traps, enough for current API.
- Vitest + Vue Test Utils for unit/component tests.
- Playwright for critical Mini App flows.
- ESLint + Prettier for consistent code before cutover.

### Routing

Use Vue Router, but start with `createWebHashHistory()` for the first production-ready Vue release.

Reason:

- Telegram Mini App does not need SEO.
- Hash routing avoids server catch-all changes during migration.
- It works under `/dygyn-bet/` and preview paths with fewer nginx/FastAPI risks.

Optional later: switch to `createWebHistory()` only after adding and testing a FastAPI/nginx SPA fallback.

### Styling

- First pass: move `web/styles.css` into Vue as global CSS with minimal changes.
- Preserve current classes during parity work where practical.
- Create design tokens in `src/assets/styles/tokens.css` only for existing colors/spacing/radii/shadows.
- Use scoped component styles sparingly during migration; avoid splitting the working design into many tiny overrides too early.
- Refactor CSS only after visual parity screenshots pass.

### State

- Use Pinia for shared server-backed domains:
  - `user` — `/api/me`, admin flag;
  - `events` — list/detail, selected event, current vote allocations;
  - `players` — list/detail cache;
  - `leaderboard` — support stats and fan rating;
  - `admin` — admin form state/actions.
- Keep short-lived UI state local to components: modal open flags, focused input, form dirtiness, loading spinners.
- Do not duplicate route state in stores unless needed for caching.

### API Types

Preferred long-term: generate client DTO types from FastAPI OpenAPI with `openapi-typescript` after key endpoints expose useful `response_model` schemas.

Practical first step: maintain manual DTOs in `src/api/types.ts` and add contract smoke tests against current API responses.

Either way:

- API module returns typed data.
- Components do not call raw `fetch`.
- API errors become one normalized `ApiError` shape.
- Backend remains the authority for auth/admin validation; `VITE_*` flags are public and not security controls.

### Telegram Integration

- Add `src/types/telegram.d.ts` for `window.Telegram.WebApp` typing.
- Initialize Telegram once at app startup: `ready()`, `expand()`.
- Read `initData` lazily from `window.Telegram?.WebApp` in API client so refreshes keep current auth.
- Support local dev with backend `ALLOW_DEV_LOGIN=true`; frontend may show a dev hint but must not fake admin/security.
- Map Telegram BackButton to router/component back behavior when inside detail screens.
- Keep haptic feedback optional and null-safe.

## Target Structure

```text
web-vue/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── playwright.config.ts
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   ├── api/
│   │   ├── client.ts
│   │   ├── events.ts
│   │   ├── players.ts
│   │   ├── leaderboard.ts
│   │   ├── admin.ts
│   │   └── types.ts
│   ├── stores/
│   │   ├── user.ts
│   │   ├── events.ts
│   │   ├── players.ts
│   │   ├── leaderboard.ts
│   │   └── admin.ts
│   ├── composables/
│   │   ├── useTelegram.ts
│   │   ├── useToast.ts
│   │   ├── useShare.ts
│   │   └── useBackButton.ts
│   ├── features/
│   │   ├── events/
│   │   ├── players/
│   │   ├── stats/
│   │   ├── story/
│   │   └── admin/
│   ├── views/
│   │   ├── EventsView.vue
│   │   ├── PlayersView.vue
│   │   ├── StatsView.vue
│   │   ├── AdminView.vue
│   │   └── RulesView.vue
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── tokens.css
│   │   │   └── main.css
│   │   └── images/
│   ├── types/
│   │   └── telegram.d.ts
│   └── test/
│       ├── setup.ts
│       └── mocks/
└── tests-e2e/
    └── critical-flows.spec.ts
```

Feature folders hold related components. Shared low-level UI components can live in `src/components/` only when reused by multiple features.

## Migration Phases

### Phase 0: Parity Baseline

Tasks:

1. Inventory current `web/app.js` behavior into a parity checklist.
2. Record key API endpoints and response shapes used by the frontend.
3. Capture screenshots for: events, selected vote, allocation validation, stats, players list, player detail, rules, admin tab, story card.
4. Add Playwright smoke against the legacy frontend if time allows; otherwise keep a manual checklist in this file or `vault/wiki/services/frontend.md`.
5. Confirm local dev command with `ALLOW_DEV_LOGIN=true`.

Verify:

- Legacy frontend still passes manual smoke.
- No production files changed except docs/tests.

Deliverable: parity checklist and screenshots ready before Vue coding.

### Phase 1: Parallel Vue Scaffold

Tasks:

1. Create `web-vue/` with Vite Vue TS template.
2. Install Vue Router, Pinia, Vitest, Vue Test Utils, Playwright, ESLint, Prettier, `vue-tsc`.
3. Commit lockfile (`package-lock.json` or chosen package-manager lockfile).
4. Configure Vite with `base: './'` for prefix-safe static assets.
5. Configure dev proxy `/api` → `http://127.0.0.1:8010`.
6. Add basic routes/tabs with empty views.
7. Keep `web/` untouched.

Verify:

- `npm run typecheck`
- `npm run build`
- `npm run test:unit`
- Vue shell loads locally.

Deliverable: empty Vue app builds independently.

### Phase 2: Foundations

Tasks:

1. Add typed API client with Telegram initData header.
2. Add API DTO types or generated OpenAPI types.
3. Add `useTelegram`, `useToast`, and `useBackButton`.
4. Add user store and `/api/me` load.
5. Port global CSS from `web/styles.css` to `src/assets/styles/main.css` with minimal edits.
6. Add route/tab shell matching current bottom navigation.
7. Add HTML escaping strategy via Vue text bindings; use `v-html` only for trusted/sanitized content.

Verify:

- Local browser with `ALLOW_DEV_LOGIN=true` loads `/api/me`.
- Telegram WebApp methods are null-safe in normal browser.
- No console errors.

Deliverable: Vue shell authenticates and visually matches the current app shell.

### Phase 3: Events Vertical Slice

Tasks:

1. Port event list and selected event detail.
2. Port public live results rendering.
3. Port participant cards and support percentages.
4. Port top-2 selection state.
5. Port 100-point allocation controls and presets.
6. Port save vote flow to `/api/events/{event_id}/prediction`.
7. Add unit tests for allocation validation and rebalancing.
8. Add Playwright flow: open app → select participant(s) → allocate 100 → save.

Verify:

- Backend accepts same payloads as legacy frontend.
- Invalid totals cannot be saved.
- Saved vote reloads with same allocations.

Deliverable: Games tab fully functional.

### Phase 4: Public Secondary Views

Tasks:

1. Port Support/leaderboard view.
2. Port Players list.
3. Port Player detail with profile badges, history, sources, and discipline tables.
4. Port Rules view and no-money copy.
5. Add component tests for player detail table rendering.

Verify:

- Public tabs match legacy screenshots.
- Rules still include no-money/votes-only language.

Deliverable: all non-admin tabs functional.

### Phase 5: Story Card and Sharing

Tasks:

1. Port canvas story-card generation into `features/story/` or `useShare`.
2. Keep same-origin participant avatar endpoint: `/api/participants/{id}/avatar`.
3. Preserve current fallback initials rendering.
4. Preserve current share behavior: native file share when available; otherwise PNG download plus Instagram instructions.
5. Add tests around share text not containing the public URL.

Verify:

- Story PNG exports with real participant photos.
- No canvas CORS errors.
- Share copy/card avoids public duckdns URL.

Deliverable: story flow matches or improves legacy behavior.

### Phase 6: Admin Panel

Tasks:

1. Gate admin route/tab from `user.is_admin`.
2. Port discipline result form.
3. Port standings form.
4. Port finish event flow.
5. Preserve admin audit logging by calling existing backend endpoints only.
6. Add Playwright/admin smoke using non-production DB and `ADMIN_IDS`/dev admin.

Verify:

- Non-admin cannot see/use admin UI.
- Admin writes succeed on test DB.
- Event public live results update after admin writes.

Deliverable: Admin tab functional and tested off production DB.

### Phase 7: Hardening and Polish

Tasks:

1. Run full parity checklist against Vue and legacy side by side.
2. Run visual screenshot comparison for main screens.
3. Run accessibility pass: semantic buttons/labels, focus states, keyboard basics, color contrast.
4. Check mobile viewport, safe-area insets, bottom nav, sticky save bar.
5. Check loading/error/empty states for every route.
6. Check performance budget.
7. Verify production build has hashed assets and no source maps unless intentionally enabled.

Verify:

- `npm run lint`
- `npm run typecheck`
- `npm run test:unit`
- `npm run test:e2e`
- `npm run build`
- Python backend tests still pass: `python -m pytest`

Deliverable: Vue app ready for VPS preview.

### Phase 8: VPS Preview Deploy

Preferred preview: serve Vue under a temporary prefix and leave production `/dygyn-bet/` on legacy.

Example nginx preview shape:

```nginx
location = /dygyn-bet-vue {
    return 301 /dygyn-bet-vue/;
}

location ^~ /dygyn-bet-vue/api/ {
    proxy_pass http://127.0.0.1:8010/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location ^~ /dygyn-bet-vue/ {
    alias /opt/dygyn-bet/web-vue/dist/;
    try_files $uri $uri/ /dygyn-bet-vue/index.html;
}
```

Tasks:

1. Build Vue on CI/local/VPS with `npm ci && npm run build`.
2. Upload `web-vue/dist/` to VPS.
3. Add temporary preview route or staging bot URL.
4. Smoke test in mobile Telegram if possible.
5. Keep legacy `/dygyn-bet/` untouched.

Verify:

- Preview loads assets under its prefix.
- Preview API calls reach existing `/api/*` backend.
- Telegram auth works over HTTPS.
- Legacy production remains healthy.

Deliverable: real-device preview without production cutover.

### Phase 9: Cutover and Rollback

Recommended cutover: keep current nginx reverse proxy for `/dygyn-bet/` and switch FastAPI static serving from `web/` to `web-vue/dist/`.

Required backend serving change:

- Add a configurable frontend directory, e.g. `FRONTEND_DIR=web` or `FRONTEND_DIR=web-vue/dist`.
- For Vue, serve `/` from `FRONTEND_DIR/index.html` with `Cache-Control: no-store`.
- Mount built assets, usually `/assets/*` → `FRONTEND_DIR/assets/*`.
- Exclude `/assets/*` from rate limiting the same way `/static/*` is currently skipped.
- Keep `/api/*`, `/health`, and avatar endpoints unchanged.
- If staying with hash router, no catch-all is required beyond `/`.
- If switching to history router later, add catch-all only after all API/static routes.

Cutover tasks:

1. Back up SQLite DB even though no DB change is expected.
2. Keep `web/` as rollback baseline; do not delete it during first release.
3. Deploy Vue dist and backend static-serving switch.
4. Restart API service and reload nginx only if config changed.
5. Run smoke checks:
   - `/dygyn-bet/health`;
   - `/dygyn-bet/`;
   - `/dygyn-bet/assets/*`;
   - `/dygyn-bet/api/me` returns 401 without auth;
   - TMA opens from bot;
   - vote save;
   - story PNG;
   - admin form on non-prod/prod only if intended.
6. Watch logs and mobile console if available.

Rollback:

1. Switch `FRONTEND_DIR` back to `web` or revert the deploy commit.
2. Restart `dygyn-bet.service`.
3. Keep DB as-is because frontend migration has no schema change.

Deliverable: Vue live on production with simple rollback.

## Key Implementation Details

### Prefix-Safe API Client

```typescript
// src/api/client.ts
type ApiOptions = RequestInit & { skipJsonContentType?: boolean }

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/$/, '')
}

const configuredBase = import.meta.env.VITE_API_BASE?.replace(/\/$/, '')
const apiBase = trimTrailingSlash(configuredBase || `${import.meta.env.BASE_URL}api`)

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { skipJsonContentType, ...requestOptions } = options
  const headers = new Headers(requestOptions.headers)
  const isForm = requestOptions.body instanceof FormData
  if (!isForm && !skipJsonContentType) headers.set('Content-Type', 'application/json')

  await ensureTelegramInit({ timeoutMs: 1800 })
  const initData = getTelegramInitData()
  if (initData) headers.set('X-Telegram-Init-Data', initData)

  const response = await fetch(`${apiBase}${path}`, { ...requestOptions, headers })
  const json = await response.json().catch(() => null)

  if (!response.ok) {
    const message = json?.detail || `HTTP ${response.status}`
    throw new ApiError(String(message), response.status, json)
  }

  return json as T
}
```

Call API modules with paths like `/me`, `/events`, `/events/${id}`. Do not call raw `fetch` in components.

### Router Config

```typescript
// src/router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/events' },
    { path: '/events', component: () => import('@/views/EventsView.vue') },
    { path: '/stats', component: () => import('@/views/StatsView.vue') },
    { path: '/players', component: () => import('@/views/PlayersView.vue') },
    { path: '/rules', component: () => import('@/views/RulesView.vue') },
    { path: '/admin', component: () => import('@/views/AdminView.vue'), meta: { requiresAdmin: true } },
  ],
})
```

Add a route guard after the user store exists; redirect non-admins away from `/admin`.

### Vite Config

```typescript
// vite.config.ts
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: './',
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8010',
    },
  },
})
```

If later using history routing and direct nginx static serving, revisit `base` and SPA fallback together.

### Package Scripts

```json
{
  "type": "module",
  "scripts": {
    "dev": "vite",
    "typecheck": "vue-tsc --noEmit",
    "build": "npm run typecheck && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier --check .",
    "test:unit": "vitest run",
    "test:e2e": "playwright test"
  }
}
```

Use current stable package versions at install time and commit the lockfile for reproducible deploys.

## Risk Register

| Risk | Mitigation | Check |
| --- | --- | --- |
| Telegram auth breaks | Initialize SDK once; lazy-read `initData`; test inside Telegram early | `/api/me` succeeds in TMA |
| Prefix paths break | `base: './'`; prefix-safe API base; preview under temp prefix | Assets/API load under `/dygyn-bet-vue/` |
| Voting regression | Unit-test allocation math; e2e save flow; keep backend validation | 1–2 picks total exactly 100 |
| CSS regression | Port CSS 1:1 first; screenshot compare before refactor | Main screens match baseline |
| Story CORS regression | Use existing avatar proxy; keep initials fallback | Canvas export works with real photos |
| Admin data damage | Admin last; non-prod DB first; audit logs unchanged | Admin smoke passes off production |
| Bundle too large | Native fetch; route lazy loading; inspect build output | Initial JS budget reviewed |
| Unsafe cutover | Parallel preview; `web/` kept; no DB schema change | Rollback = switch frontend dir back |

## Success Criteria

- [ ] Vue app reaches feature parity with current `web/`.
- [ ] Existing FastAPI tests pass.
- [ ] `npm run lint`, `typecheck`, `test:unit`, `test:e2e`, and `build` pass.
- [ ] Telegram auth works in production TMA.
- [ ] Vote save works for 1–2 participants and exactly 100 confidence points.
- [ ] Story card exports with real participant photos and no public URL text.
- [ ] Admin tab works only for `ADMIN_IDS`.
- [ ] No console errors in production smoke.
- [ ] Mobile UI keeps bottom nav/sticky save safe-area behavior.
- [ ] Rules/no-money language remains visible.
- [ ] Legacy rollback remains available after first cutover.

## Timeline Estimate

- Phase 0: 0.5–1 day.
- Phase 1: 0.5–1 day.
- Phase 2: 1–2 days.
- Phase 3: 3–4 days.
- Phase 4: 2–3 days.
- Phase 5: 1–2 days.
- Phase 6: 2–3 days.
- Phase 7: 2–3 days.
- Phase 8: 0.5–1 day.
- Phase 9: 0.5–1 day.

Total: 13–21 days depending on testing depth and Telegram device QA.

## Next Steps

1. Run real mobile Telegram QA on branch `vue-tma-cutover`, especially delayed SDK auth, vote save, story share, and admin forms.
2. Build on VPS with `cd web-vue && npm ci && npm run build`.
3. Set/confirm `FRONTEND_DIR=/opt/dygyn-bet/web-vue/dist`; rollback remains `FRONTEND_DIR=web`.
4. Deploy only after QA passes.
