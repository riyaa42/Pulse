# MusicDB

Main navigation map for the MusicDB project.

## Project at a glance

MusicDB is a database-first music streaming and event management system with:

- MySQL schema and SQL logic (`data/`)
- FastAPI backend (`backend/`)
- SvelteKit frontend (`frontend/`)
- media asset storage (`media/`)
- report documents (`docs/`)

## Folder navigation map

- `backend/`
  - API server code, DB access logic, app settings
  - See `backend/BACKEND_README.md`
- `frontend/`
  - SvelteKit UI routes, session/player state, API integration
  - See `frontend/FRONTEND_README.md`
- `data/`
  - SQL dump, extension SQL, Workbench model
  - See `data/DATA_README.md`
- `media/`
  - album/artist/track/show/user assets and placeholders
  - See `media/MEDIA_README.md`
- `docs/`
  - project PDF reports and submission-ready documents
  - See `docs/DOCS_README.md`
- `run.sh`
  - convenience script to install dependencies and run backend + frontend

## Quick start

1) Database setup

```bash
mysql -u root -p < data/musicdb.sql
mysql -u root -p < data/app_extensions.sql
```

2) Run full app

```bash
./run.sh
```

3) Open

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/api/health`

## Stored Procedures & Triggers

The backend uses SQL stored procedures and triggers for business logic:

**Procedures (called explicitly):**
- `BookTicketWithValidation()` - books ticket with duplicate seat validation
- `RecordStreamWithRoyaltyUpdate()` - records stream and updates royalty count
- `EndStreamEvent()` - ends a stream event

**Functions (used in queries):**
- `GetAlbumDuration(album_id)` - returns total duration of album tracks
- `GetAlbumTrackCount(album_id)` - returns track count for album

**Triggers (auto-fired by MySQL):**
- `prevent_duplicate_seat_booking` - blocks duplicate seat booking on INSERT
- `after_stream_insert` - auto-updates royalty StreamCount on stream INSERT
- `before_user_follow_insert` - blocks self-follow
- `before_artist_follow_insert` - blocks duplicate artist follow