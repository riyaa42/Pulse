# Backend README

FastAPI backend for MusicDB. This layer exposes REST endpoints over the MySQL schema in `../data/` and serves local media URLs from `../media/`.

## What this folder contains

- `main.py` - backend entry point (`uvicorn` launcher).
- `pyproject.toml` - project metadata and Python dependencies.
- `uv.lock` - locked dependency versions.
- `app/` - application source code.
  - `app/main.py` - API routes, request models, business logic.
  - `app/db.py` - MySQL pooled connection helpers.
  - `app/config.py` - environment-based settings.
  - `app/assets.py` - media file resolution rules.

## Setup

1) Install dependencies

```bash
uv sync
```

2) Load database schema and extension objects

```bash
mysql -u root -p < ../data/musicdb.sql
mysql -u root -p < ../data/app_extensions.sql
```

3) Create `backend/.env`

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=musicdb
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_PUBLIC_URL=http://localhost:8000
MEDIA_ROOT=../media
MEDIA_URL_PREFIX=/media
```

4) Run backend

```bash
uv run python main.py
```

## Major API groups

- Session/bootstrap: `/api/session/options`, `/api/me`, `/api/bootstrap`
- Discovery: `/api/search`, `/api/top-songs`, `/api/events/upcoming`, `/api/tags`
- Albums: `/api/albums/{id}` - album details with tracks
- Listener actions: playlists, follows, streams, ticket booking, profile/settings
- Artist actions: dashboard, catalog CRUD (albums/tracks/tags/credits), show management
- Media spec: `/api/assets/spec`

## Stored Procedures & Triggers

The backend uses SQL stored procedures and triggers (defined in `../data/app_extensions.sql`) instead of manual SQL logic:

**Procedures (called via `cursor.callproc()`):**
| Endpoint | Procedure | Purpose |
|----------|-----------|---------|
| `POST /api/shows/{id}/book` | `BookTicketWithValidation()` | Books ticket with duplicate seat check |
| `POST /api/streams/start` | `RecordStreamWithRoyaltyUpdate()` | Records stream + updates royalty |
| `POST /api/streams/end` | `EndStreamEvent()` | Ends stream event |

**Functions (used in SELECT queries):**
- `GetAlbumDuration(album_id)` - returns total duration of album tracks
- `GetAlbumTrackCount(album_id)` - returns track count for album

**Triggers (auto-fired on DML operations):**
- `prevent_duplicate_seat_booking` - BEFORE INSERT on `ticket` table
- `after_stream_insert` - AFTER INSERT on `streamlog` table
- `before_user_follow_insert` - BEFORE INSERT on `user_follow` table
- `before_artist_follow_insert` - BEFORE INSERT on `artist_follow` table

For media folder structure and naming, see `../media/MEDIA_README.md`.