# Data README

This folder contains SQL/database design artifacts for MusicDB.

## What this folder contains

- `musicdb.sql` - base schema + seed data dump (core project database).
- `app_extensions.sql` - additional app-layer tables, stored procedures, functions, triggers, and seed mappings used by current backend features.
- `musicstreamingdb.mwb` - MySQL Workbench model file.

## Load order

Run these in order when setting up a fresh database:

```bash
mysql -u root -p < musicdb.sql
mysql -u root -p < app_extensions.sql
```

## Stored Procedures & Triggers

This file defines all SQL routines used by the backend:

### Functions

```sql
GetUserFollowerCount(p_user_id INT) -> INT
GetUserFollowingCount(p_user_id INT) -> INT
GetArtistFollowerCount(p_artist_id INT) -> INT
GetTrackTotalStreams(p_track_id INT) -> INT
GetAlbumDuration(p_album_id INT) -> INT
GetAlbumTrackCount(p_album_id INT) -> INT
```

### Stored Procedures

```sql
RecordStreamEvent(p_user_id, p_track_id, p_device_type, p_country)
RecordStreamWithRoyaltyUpdate(p_user_id, p_track_id, p_device_type, p_country)
EndStreamEvent(p_stream_id, p_user_id, p_was_completed, p_skipped_at)
BookTicketWithValidation(p_user_id, p_show_id, p_price, p_seat_section, p_seat_row, p_seat_number, p_seat_category)
CancelTicketBooking(p_ticket_id, p_user_id)
RefreshRoyaltyStreamCounts()
```

### Triggers

```sql
-- Auto-fired on DML operations
prevent_duplicate_seat_booking  -- BEFORE INSERT on ticket
after_stream_insert           -- AFTER INSERT on streamlog
before_user_follow_insert   -- BEFORE INSERT on user_follow
before_artist_follow_insert -- BEFORE INSERT on artist_follow
```

## Database Schema Overview

**Core tables:**
- `users` - listener accounts
- `artist` - artist profiles
- `album` - albums
- `track` - tracks
- `playlist` / `playlisttrack` - playlists
- `streamlog` - streaming events
- `show` - artist shows
- `ticket` - show bookings

**Extension tables:**
- `artist_user` - user-artist role mapping
- `user_follow` / `artist_follow` - follow relationships
- `artistalbum` - album-artist links
- `albumtag` / `tracktag` - genre/mood tags
- `subscription` / `linkeddevices` - listener features
- `royalty` - artist royalty tracking