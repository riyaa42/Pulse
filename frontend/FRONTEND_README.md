# Frontend README

SvelteKit frontend for MusicDB. This app consumes the backend APIs, supports listener and artist modes, and renders playlist, search, profile, ticket, and artist studio flows.

## What this folder contains

- `package.json` - scripts and frontend dependencies.
- `package-lock.json` - npm lockfile.
- `svelte.config.js`, `vite.config.ts`, `tsconfig.json` - framework/build config.
- `src/` - application source.
  - `src/routes/+layout.svelte` - global shell, nav, side rails, player strip.
  - `src/routes/+page.svelte` - home page (listener + artist studio views).
  - `src/routes/search/` - search and filters UI.
  - `src/routes/artist/[id]/` - public artist profile and shows.
  - `src/routes/user/[id]/` - user profile, settings, subscriptions, devices, tickets.
  - `src/routes/playlist/[id]/` - playlist detail and track management.
  - `src/lib/api.ts` - API client + actor header handling.
  - `src/lib/session.ts` - session hydration and actor switching.
  - `src/lib/player.ts` - now-playing state store.
- `static/` - static assets (`robots.txt`).
- `node_modules/` - installed packages (generated).

## Setup

```sh
npm install
```

Create `frontend/.env`:

```env
PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run

```sh
npm run dev
```

## Checks and build

```sh
npm run check
npm run build
```
