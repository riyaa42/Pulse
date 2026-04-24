import logging
from typing import Any

import mysql.connector
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.assets import (
    AUDIO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    resolve_image_url,
    resolve_track_audio_url,
)
from app.config import settings
from app.db import execute, fetch_all, fetch_one, get_connection, call_proc


app = FastAPI(title="MusicDB API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.media_url_prefix, StaticFiles(directory=settings.media_root), name="media")

logger = logging.getLogger(__name__)


def _disable_broken_case_sensitive_triggers() -> None:
    """Remove legacy triggers with mixed-case table references that conflict with new schema."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TRIGGER IF EXISTS after_stream_insert")
                cursor.execute("DROP TRIGGER IF EXISTS prevent_duplicate_seat_booking")
            conn.commit()
    except mysql.connector.Error as exc:
        logger.warning("Could not remove legacy triggers automatically: %s", exc)


@app.on_event("startup")
def _on_startup() -> None:
    _disable_broken_case_sensitive_triggers()


class TicketBookingPayload(BaseModel):
    seat_section: str
    seat_row: str
    seat_number: str
    seat_category: str


class FollowArtistPayload(BaseModel):
    artist_id: int


class StreamStartPayload(BaseModel):
    track_id: int
    device_type: str = "Web"
    country: str = "Unknown"


class FollowUserPayload(BaseModel):
    followed_user_id: int


class PlaylistTrackPayload(BaseModel):
    track_id: int


class PlaylistCreatePayload(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = True
    is_collaborative: bool = False


class ArtistAlbumCreatePayload(BaseModel):
    title: str
    release_date: str | None = None
    language: str | None = None
    album_type: str | None = "Studio Album"
    cover_image: str | None = None


class ArtistTrackCreatePayload(BaseModel):
    title: str
    duration: int | None = None
    language: str | None = None
    release_date: str | None = None
    bpm: int | None = None
    album_id: int | None = None
    lyrics: str | None = "Lyrics pending"
    tag_ids: list[int] = Field(default_factory=list)
    tag_names: list[str] = Field(default_factory=list)


class ArtistShowCreatePayload(BaseModel):
    title: str
    description: str | None = None
    show_date: str
    show_time: str
    venue_name: str | None = None
    venue_city: str | None = None
    venue_country: str | None = None
    status: str = "Scheduled"


class StreamEndPayload(BaseModel):
    stream_id: int
    completed: bool = False
    skipped_at: int | None = None


class AlbumTagsPayload(BaseModel):
    tag_ids: list[int] = Field(default_factory=list)
    tag_names: list[str] = Field(default_factory=list)


class ArtistShowUpdatePayload(BaseModel):
    title: str | None = None
    description: str | None = None
    show_date: str | None = None
    show_time: str | None = None
    venue_name: str | None = None
    venue_city: str | None = None
    venue_country: str | None = None
    status: str | None = None


class TrackCreditPayload(BaseModel):
    person_name: str
    role: str
    entity_type: str = "Track"


class DevicePayload(BaseModel):
    device_type: str
    device_name: str | None = None


class NotificationPreferencePayload(BaseModel):
    notification_type: str
    enabled: bool = True


class SubscriptionChangePayload(BaseModel):
    plan_id: int


def _mysql_error(exc: mysql.connector.Error) -> None:
    raise HTTPException(status_code=400, detail=str(exc)) from exc


def _get_actor(request: Request) -> dict[str, Any]:
    actor_type = request.headers.get("x-actor-type", "listener").strip().lower()
    actor_id_raw = request.headers.get("x-actor-id", request.headers.get("x-user-id", "1")).strip()
    if actor_type not in {"listener", "artist"}:
        raise HTTPException(status_code=400, detail="Invalid x-actor-type header")
    if not actor_id_raw.isdigit():
        raise HTTPException(status_code=400, detail="Invalid x-actor-id header")
    actor_id = int(actor_id_raw)

    if actor_type == "listener":
        actor = fetch_one(
            """
            SELECT
                u.UserID AS user_id,
                u.Username AS username,
                u.Country AS country,
                u.ProfileImage AS profile_image
            FROM users u
            WHERE u.UserID = %s
            """,
            (actor_id,),
        )
        if not actor:
            raise HTTPException(status_code=404, detail="Listener not found")
        actor["actor_type"] = "listener"
        actor["role"] = "listener"
        actor["artist_id"] = None
        actor["profile_image_url"] = resolve_image_url(
            "user_profile",
            filename=actor.get("profile_image"),
            stems=(f"user_{actor['user_id']}", str(actor["user_id"])),
        )
        return actor

    actor = fetch_one(
        """
        SELECT
            a.ArtistID AS artist_id,
            a.StageName AS username,
            a.Country AS country,
            a.ProfileImage AS profile_image
        FROM artist a
        WHERE a.ArtistID = %s
        """,
        (actor_id,),
    )
    if not actor:
        raise HTTPException(status_code=404, detail="Artist not found")
    actor["actor_type"] = "artist"
    actor["role"] = "artist"
    actor["user_id"] = None
    actor["profile_image_url"] = resolve_image_url(
        "artist_profile",
        filename=actor.get("profile_image"),
        stems=(f"artist_{actor['artist_id']}", str(actor["artist_id"])),
    )
    return actor


def _require_listener_actor(request: Request) -> dict[str, Any]:
    actor = _get_actor(request)
    if actor["actor_type"] != "listener":
        raise HTTPException(status_code=403, detail="Listener login required")
    return actor


def _require_artist_actor(request: Request) -> dict[str, Any]:
    actor = _get_actor(request)
    if actor["actor_type"] != "artist":
        raise HTTPException(status_code=403, detail="Artist role required")
    return actor


def _track_assets(row: dict[str, Any]) -> dict[str, Any]:
    track_id = int(row.get("track_id", 0))
    album_id = row.get("album_id")
    cover_name = row.get("cover_image")
    row["album_cover_url"] = resolve_image_url(
        "album_cover",
        filename=cover_name,
        stems=(f"album_{album_id}", str(album_id), f"track_{track_id}", str(track_id)),
    )
    row["track_cover_url"] = resolve_image_url(
        "track_cover",
        filename=row.get("track_image"),
        stems=(f"track_{track_id}", str(track_id)),
    )
    row["audio_url"] = resolve_track_audio_url(track_id, filename=row.get("audio_file"))
    return row


def _normalize_tag_names(tag_names: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in tag_names:
        clean = raw.strip()
        if not clean:
            continue
        key = clean.casefold()
        if key in seen:
            continue
        normalized.append(clean)
        seen.add(key)
    return normalized


def _resolve_tag_ids(cursor: Any, tag_ids: list[int], tag_names: list[str]) -> list[int]:
    resolved: list[int] = []
    seen_ids: set[int] = set()

    for tag_id in tag_ids:
        if tag_id <= 0 or tag_id in seen_ids:
            continue
        cursor.execute("SELECT TagID AS tag_id FROM tag WHERE TagID = %s", (tag_id,))
        existing = cursor.fetchone()
        if existing:
            resolved.append(int(existing["tag_id"]))
            seen_ids.add(int(existing["tag_id"]))

    for tag_name in _normalize_tag_names(tag_names):
        cursor.execute(
            "SELECT TagID AS tag_id FROM tag WHERE LOWER(TagName) = LOWER(%s) ORDER BY TagID ASC LIMIT 1",
            (tag_name,),
        )
        existing = cursor.fetchone()
        if existing:
            tag_id = int(existing["tag_id"])
        else:
            cursor.execute("INSERT INTO tag (TagName) VALUES (%s)", (tag_name,))
            tag_id = int(cursor.lastrowid)
        if tag_id not in seen_ids:
            resolved.append(tag_id)
            seen_ids.add(tag_id)

    return resolved


@app.get("/api/health")
def health() -> dict[str, str]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {"status": "ok"}
    except mysql.connector.Error:
        return {"status": "degraded", "db": "unreachable"}


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    users = fetch_all(
            "SELECT UserID AS id, Username AS username, Country AS country, ProfileImage AS profile_image FROM users ORDER BY UserID"
        )
    for row in users:
        row["profile_image_url"] = resolve_image_url(
            "user_profile",
            filename=row.get("profile_image"),
            stems=(f"user_{row['id']}", str(row["id"])),
        )

    artists = fetch_all(
            "SELECT ArtistID AS id, StageName AS stage_name, Country AS country, ProfileImage AS profile_image FROM artist ORDER BY ArtistID"
        )
    for row in artists:
        row["profile_image_url"] = resolve_image_url(
            "artist_profile",
            filename=row.get("profile_image"),
            stems=(f"artist_{row['id']}", str(row["id"])),
        )
        row["header_image_url"] = resolve_image_url(
            "artist_header",
            stems=(f"artist_{row['id']}", str(row["id"])),
        )

    return {
        "users": users,
        "artists": artists,
        "tags": fetch_all("SELECT TagID AS id, TagName AS name FROM tag ORDER BY TagName"),
    }


@app.get("/api/session/options")
def session_options() -> dict[str, Any]:
    listeners = fetch_all(
        """
        SELECT
            u.UserID AS user_id,
            u.Username AS username,
            u.Country AS country,
            u.ProfileImage AS profile_image
        FROM users u
        ORDER BY u.UserID
        """
    )
    for row in listeners:
        row["actor_type"] = "listener"
        row["profile_image_url"] = resolve_image_url(
            "user_profile",
            filename=row.get("profile_image"),
            stems=(f"user_{row['user_id']}", str(row["user_id"])),
        )

    artists = fetch_all(
        """
        SELECT
            a.ArtistID AS artist_id,
            a.StageName AS stage_name,
            a.Country AS country,
            a.ProfileImage AS profile_image
        FROM artist a
        ORDER BY a.ArtistID
        """
    )
    for row in artists:
        row["actor_type"] = "artist"
        row["profile_image_url"] = resolve_image_url(
            "artist_profile",
            filename=row.get("profile_image"),
            stems=(f"artist_{row['artist_id']}", str(row["artist_id"])),
        )

    return {"listeners": listeners, "artists": artists}


@app.get("/api/me")
def me(request: Request) -> dict[str, Any]:
    return _get_actor(request)


@app.get("/api/me/library")
def my_library(request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    playlists = fetch_all(
        """
        SELECT
            p.PlaylistID AS playlist_id,
            p.Name AS name,
            p.Description AS description,
            p.IsPublic AS is_public,
            COUNT(pt.Track_TrackID) AS tracks_count
        FROM playlist p
        LEFT JOIN playlisttrack pt ON pt.Playlist_PlaylistID = p.PlaylistID
        WHERE p.Users_UserID = %s
        GROUP BY p.PlaylistID, p.Name, p.Description, p.IsPublic
        ORDER BY p.CreatedAt DESC, p.Name ASC
        """,
        (actor["user_id"],),
    )
    return {"playlists": playlists}


@app.get("/api/plans")
def plans() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            p.PlanID AS plan_id,
            p.PlanName AS plan_name,
            p.Price AS price,
            p.Currency AS currency,
            p.Features AS features,
            p.MaxDevices AS max_devices
        FROM plan p
        ORDER BY p.Price ASC
        """
    )


@app.get("/api/me/settings")
def my_settings(request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    user_id = actor["user_id"]
    devices = fetch_all(
        """
        SELECT
            ld.DeviceID AS device_id,
            ld.DeviceType AS device_type,
            ld.DeviceName AS device_name,
            ld.LastUsed AS last_used
        FROM linkeddevices ld
        WHERE ld.Users_UserID = %s
        ORDER BY ld.LastUsed DESC, ld.DeviceID DESC
        """,
        (user_id,),
    )
    notification_preferences = fetch_all(
        """
        SELECT
            np.NotificationID AS notification_id,
            np.NotificationType AS notification_type
        FROM notificationpreferences np
        WHERE np.Users_UserID = %s
        ORDER BY np.NotificationType ASC
        """,
        (user_id,),
    )
    current_subscription = fetch_one(
        """
        SELECT
            s.SubscriptionID AS subscription_id,
            s.Status AS status,
            s.StartDate AS start_date,
            s.EndDate AS end_date,
            s.AutoRenewal AS auto_renewal,
            s.NextBillingDate AS next_billing_date,
            p.PlanID AS plan_id,
            p.PlanName AS plan_name,
            p.Price AS price,
            p.Currency AS currency,
            p.Features AS features,
            p.MaxDevices AS max_devices
        FROM subscription s
        JOIN plan p ON p.PlanID = s.Plan_PlanID
        WHERE s.Users_UserID = %s
        """,
        (user_id,),
    )
    return {
        "devices": devices,
        "notification_preferences": notification_preferences,
        "subscription": current_subscription,
        "plans": plans(),
    }


@app.post("/api/me/subscription")
def change_subscription(payload: SubscriptionChangePayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    plan = fetch_one(
        """
        SELECT
            p.PlanID AS plan_id,
            p.PlanName AS plan_name,
            p.Price AS price,
            p.Currency AS currency,
            p.Features AS features,
            p.MaxDevices AS max_devices
        FROM plan p
        WHERE p.PlanID = %s
        """,
        (payload.plan_id,),
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                existing = fetch_one(
                    "SELECT SubscriptionID AS subscription_id FROM subscription WHERE Users_UserID = %s",
                    (actor["user_id"],),
                )
                if existing:
                    cursor.execute(
                        """
                        UPDATE subscription
                        SET Plan_PlanID = %s,
                            Status = 'Active',
                            NextBillingDate = DATE_ADD(NOW(), INTERVAL 1 MONTH)
                        WHERE Users_UserID = %s
                        """,
                        (payload.plan_id, actor["user_id"]),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO subscription
                        (StartDate, EndDate, AutoRenewal, Status, NextBillingDate, Plan_PlanID, Users_UserID)
                        VALUES (NOW(), DATE_ADD(NOW(), INTERVAL 1 MONTH), 1, 'Active', DATE_ADD(NOW(), INTERVAL 1 MONTH), %s, %s)
                        """,
                        (payload.plan_id, actor["user_id"]),
                    )
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Subscription updated", "plan": plan}


@app.post("/api/me/devices")
def add_device(payload: DevicePayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO linkeddevices (DeviceType, DeviceName, LastUsed, Users_UserID)
                    VALUES (%s, %s, NOW(), %s)
                    """,
                    (payload.device_type, payload.device_name, actor["user_id"]),
                )
                conn.commit()
                device_id = cursor.lastrowid
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Device linked", "device_id": device_id}


@app.delete("/api/me/devices/{device_id}")
def remove_device(device_id: int, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        removed = execute(
            "DELETE FROM linkeddevices WHERE DeviceID = %s AND Users_UserID = %s",
            (device_id, actor["user_id"]),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if removed == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device removed"}


@app.post("/api/me/notification-preferences")
def upsert_notification_preference(payload: NotificationPreferencePayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        if payload.enabled:
            execute(
                """
                INSERT INTO notificationpreferences (NotificationType, Users_UserID)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM notificationpreferences
                    WHERE NotificationType = %s AND Users_UserID = %s
                )
                """,
                (payload.notification_type, actor["user_id"], payload.notification_type, actor["user_id"]),
            )
            return {"message": "Notification preference enabled"}

        execute(
            "DELETE FROM notificationpreferences WHERE NotificationType = %s AND Users_UserID = %s",
            (payload.notification_type, actor["user_id"]),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Notification preference disabled"}


@app.get("/api/assets/spec")
def assets_spec() -> dict[str, Any]:
    return {
        "media_root": settings.media_root,
        "media_url_prefix": settings.media_url_prefix,
        "image_extensions": list(IMAGE_EXTENSIONS),
        "audio_extensions": list(AUDIO_EXTENSIONS),
        "image_slots": {
            "user_profile": "users/profiles",
            "artist_profile": "artists/profiles",
            "artist_header": "artists/headers",
            "album_cover": "albums/covers",
            "track_cover": "tracks/covers",
            "show_poster": "shows/posters",
        },
        "audio_slots": {
            "track_audio": "tracks/audio",
        },
    }


@app.get("/api/tags")
def tags() -> list[dict[str, Any]]:
    return fetch_all("SELECT TagID AS id, TagName AS name FROM tag ORDER BY TagName")


@app.get("/api/top-songs")
def top_songs(limit: int = 10) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Album_AlbumID AS album_id,
            a.Title AS album_title,
            a.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM track t
        LEFT JOIN album a ON a.AlbumID = t.Album_AlbumID
        LEFT JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        LEFT JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        GROUP BY t.TrackID, t.Title, t.Album_AlbumID, a.Title, a.CoverImage, ar.ArtistID, ar.StageName
        ORDER BY total_streams DESC, t.Title ASC
        LIMIT %s
        """,
        (limit,),
    )
    return [_track_assets(row) for row in rows]


@app.get("/api/search")
def search(tag_id: int | None = None, q: str = "") -> dict[str, Any]:
    like = f"%{q.strip()}%"
    tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Duration AS duration,
            t.Language AS language,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            GROUP_CONCAT(DISTINCT tg.TagName ORDER BY tg.TagName SEPARATOR ', ') AS tags,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM track t
        LEFT JOIN album al ON al.AlbumID = t.Album_AlbumID
        LEFT JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        LEFT JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        LEFT JOIN tracktag tt ON tt.Track_TrackID = t.TrackID
        LEFT JOIN tag tg ON tg.TagID = tt.Tag_TagID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        WHERE (%s = '' OR t.Title LIKE %s OR al.Title LIKE %s)
          AND (%s IS NULL OR EXISTS (
              SELECT 1 FROM tracktag x WHERE x.Track_TrackID = t.TrackID AND x.Tag_TagID = %s
          ))
        GROUP BY t.TrackID, t.Title, t.Duration, t.Language, t.Album_AlbumID, al.Title, al.CoverImage, ar.ArtistID, ar.StageName
        ORDER BY total_streams DESC, t.Title ASC
        """,
        (q.strip(), like, like, tag_id, tag_id),
    )
    albums = fetch_all(
        """
        SELECT
            al.AlbumID AS album_id,
            al.Title AS title,
            al.ReleaseDate AS release_date,
            al.Language AS language,
            al.AlbumType AS album_type,
            al.CoverImage AS cover_image,
            GROUP_CONCAT(DISTINCT tg.TagName ORDER BY tg.TagName SEPARATOR ', ') AS tags,
            COUNT(DISTINCT t.TrackID) AS tracks_count
        FROM album al
        LEFT JOIN track t ON t.Album_AlbumID = al.AlbumID
        LEFT JOIN albumtag atg ON atg.Album_AlbumID = al.AlbumID
        LEFT JOIN tag tg ON tg.TagID = atg.Tag_TagID
        WHERE (%s = '' OR al.Title LIKE %s)
          AND (%s IS NULL OR EXISTS (
              SELECT 1 FROM albumtag x WHERE x.Album_AlbumID = al.AlbumID AND x.Tag_TagID = %s
          ))
        GROUP BY al.AlbumID, al.Title, al.ReleaseDate, al.Language, al.AlbumType, al.CoverImage
        ORDER BY al.ReleaseDate DESC, al.Title ASC
        """,
        (q.strip(), like, tag_id, tag_id),
    )
    tracks = [_track_assets(row) for row in tracks]
    for row in albums:
        album_id = row.get("album_id")
        row["album_cover_url"] = resolve_image_url(
            "album_cover",
            filename=row.get("cover_image"),
            stems=(f"album_{album_id}", str(album_id)),
        )
    return {"tracks": tracks, "albums": albums}


@app.get("/api/events/upcoming")
def upcoming_events() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT
            s.ShowID AS show_id,
            s.Title AS title,
            s.Description AS description,
            s.ShowDate AS show_date,
            s.ShowTime AS show_time,
            s.VenuName AS venue_name,
            s.VenueCity AS venue_city,
            s.VenueCountry AS venue_country,
            s.Status AS status,
            a.ArtistID AS artist_id,
            a.StageName AS artist_name,
            SUM(CASE WHEN COALESCE(t.Status, 'Booked') <> 'Cancelled' THEN 1 ELSE 0 END) AS booked_tickets
        FROM `show` s
        JOIN artist a ON a.ArtistID = s.Artist_ArtistID
        LEFT JOIN ticket t ON t.Show_ShowID = s.ShowID
        GROUP BY s.ShowID, s.Title, s.Description, s.ShowDate, s.ShowTime, s.VenuName, s.VenueCity, s.VenueCountry,
                 s.Status, a.ArtistID, a.StageName
        ORDER BY s.ShowDate ASC, s.ShowTime ASC
        """
    )
    for row in rows:
        row["poster_image_url"] = resolve_image_url(
            "show_poster",
            stems=(f"show_{row['show_id']}", str(row["show_id"])),
        )
    return rows


@app.get("/api/playlists/{playlist_id}")
def playlist_details(playlist_id: int, request: Request) -> dict[str, Any]:
    actor = _get_actor(request)
    playlist = fetch_one(
        """
        SELECT
            p.PlaylistID AS playlist_id,
            p.Name AS name,
            p.Description AS description,
            p.IsPublic AS is_public,
            p.Users_UserID AS owner_user_id,
            u.Username AS owner_username,
            COUNT(pt.Track_TrackID) AS tracks_count
        FROM playlist p
        JOIN users u ON u.UserID = p.Users_UserID
        LEFT JOIN playlisttrack pt ON pt.Playlist_PlaylistID = p.PlaylistID
        WHERE p.PlaylistID = %s
        GROUP BY p.PlaylistID, p.Name, p.Description, p.IsPublic, p.Users_UserID, u.Username
        """,
        (playlist_id,),
    )
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if not playlist["is_public"] and actor.get("user_id") != playlist["owner_user_id"]:
        raise HTTPException(status_code=403, detail="Private playlist")

    tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Duration AS duration,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            pt.AddedAt AS added_at,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM playlisttrack pt
        JOIN track t ON t.TrackID = pt.Track_TrackID
        LEFT JOIN album al ON al.AlbumID = t.Album_AlbumID
        LEFT JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        LEFT JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        WHERE pt.Playlist_PlaylistID = %s
        GROUP BY t.TrackID, t.Title, t.Duration, t.Album_AlbumID, al.Title, al.CoverImage, ar.ArtistID, ar.StageName, pt.AddedAt
        ORDER BY pt.AddedAt DESC, t.Title ASC
        """,
        (playlist_id,),
    )
    tracks = [_track_assets(row) for row in tracks]
    playlist["can_edit"] = playlist["owner_user_id"] == actor.get("user_id")
    return {"playlist": playlist, "tracks": tracks}


@app.post("/api/playlists")
def create_playlist(payload: PlaylistCreatePayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO playlist (Name, Description, CreatedAt, IsPublic, IsCollaborative, Users_UserID)
                    VALUES (%s, %s, NOW(), %s, %s, %s)
                    """,
                    (
                        payload.name,
                        payload.description,
                        1 if payload.is_public else 0,
                        1 if payload.is_collaborative else 0,
                        actor["user_id"],
                    ),
                )
                conn.commit()
                playlist_id = cursor.lastrowid
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Playlist created", "playlist_id": playlist_id}


@app.post("/api/playlists/{playlist_id}/tracks")
def add_track_to_playlist(playlist_id: int, payload: PlaylistTrackPayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    playlist = fetch_one(
        "SELECT PlaylistID AS playlist_id FROM playlist WHERE PlaylistID = %s AND Users_UserID = %s",
        (playlist_id, actor["user_id"]),
    )
    if not playlist:
        raise HTTPException(status_code=403, detail="You can only edit your own playlists")
    track = fetch_one("SELECT TrackID AS track_id FROM track WHERE TrackID = %s", (payload.track_id,))
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        execute(
            """
            INSERT INTO playlisttrack (AddedAt, Playlist_PlaylistID, Track_TrackID)
            VALUES (NOW(), %s, %s)
            """,
            (playlist_id, payload.track_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Track added to playlist"}


@app.delete("/api/playlists/{playlist_id}/tracks/{track_id}")
def remove_track_from_playlist(playlist_id: int, track_id: int, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    owner = fetch_one(
        "SELECT PlaylistID AS playlist_id FROM playlist WHERE PlaylistID = %s AND Users_UserID = %s",
        (playlist_id, actor["user_id"]),
    )
    if not owner:
        raise HTTPException(status_code=403, detail="You can only edit your own playlists")
    try:
        removed = execute(
            "DELETE FROM playlisttrack WHERE Playlist_PlaylistID = %s AND Track_TrackID = %s",
            (playlist_id, track_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if removed == 0:
        raise HTTPException(status_code=404, detail="Track not found in playlist")
    return {"message": "Track removed from playlist"}


@app.delete("/api/playlists/{playlist_id}")
def delete_playlist(playlist_id: int, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT PlaylistID FROM playlist WHERE PlaylistID = %s AND Users_UserID = %s",
                    (playlist_id, actor["user_id"]),
                )
                owner = cursor.fetchone()
                if not owner:
                    raise HTTPException(status_code=404, detail="Playlist not found")
                cursor.execute(
                    "DELETE FROM playlisttrack WHERE Playlist_PlaylistID = %s",
                    (playlist_id,),
                )
                cursor.execute(
                    "DELETE FROM playlist WHERE PlaylistID = %s AND Users_UserID = %s",
                    (playlist_id, actor["user_id"]),
                )
                removed = cursor.rowcount
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Playlist deleted"}


@app.get("/api/tracks/{track_id}/context")
def track_context(track_id: int) -> dict[str, Any]:
    track = fetch_one(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            ar.Bio AS artist_bio,
            ar.ProfileImage AS artist_profile_image
        FROM track t
        LEFT JOIN album al ON al.AlbumID = t.Album_AlbumID
        LEFT JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        LEFT JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        WHERE t.TrackID = %s
        """,
        (track_id,),
    )
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    track = _track_assets(track)
    artist_id = track.get("artist_id")
    if artist_id:
        track["artist_profile_url"] = resolve_image_url(
            "artist_profile",
            filename=track.get("artist_profile_image"),
            stems=(f"artist_{artist_id}", str(artist_id)),
        )
    related_tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM track t
        LEFT JOIN album al ON al.AlbumID = t.Album_AlbumID
        LEFT JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        LEFT JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        WHERE (%s IS NULL OR ar.ArtistID = %s)
          AND t.TrackID <> %s
        GROUP BY t.TrackID, t.Title, t.Album_AlbumID, al.Title, al.CoverImage, ar.ArtistID, ar.StageName
        ORDER BY total_streams DESC, t.Title ASC
        LIMIT 8
        """,
        (artist_id, artist_id, track_id),
    )
    related_tracks = [_track_assets(row) for row in related_tracks]
    return {"track": track, "related_tracks": related_tracks}


@app.get("/api/artists")
def artists() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT
            ar.ArtistID AS artist_id,
            ar.StageName AS stage_name,
            ar.Country AS country,
            ar.ProfileImage AS profile_image,
            ar.VerificationStatus AS verification_status,
            (
                SELECT COUNT(*) FROM artist_follow af WHERE af.ArtistID = ar.ArtistID
            ) AS followers,
            (
                SELECT COUNT(*)
                FROM streamlog sl
                JOIN track t ON t.TrackID = sl.Track_TrackID
                JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
                WHERE aa.Artist_ArtistID = ar.ArtistID
            ) AS total_streams
        FROM artist ar
        ORDER BY followers DESC, ar.StageName ASC
        """
    )
    for row in rows:
        artist_id = row["artist_id"]
        row["profile_image_url"] = resolve_image_url(
            "artist_profile",
            filename=row.get("profile_image"),
            stems=(f"artist_{artist_id}", str(artist_id)),
        )
        row["header_image_url"] = resolve_image_url(
            "artist_header",
            stems=(f"artist_{artist_id}", str(artist_id)),
        )
    return rows


@app.get("/api/artists/{artist_id}")
def artist_profile(artist_id: int, request: Request) -> dict[str, Any]:
    actor = _get_actor(request)
    artist = fetch_one(
        """
        SELECT
            ar.ArtistID AS artist_id,
            ar.StageName AS stage_name,
            ar.FirstName AS first_name,
            ar.LastName AS last_name,
            ar.Bio AS bio,
            ar.Country AS country,
            ar.ProfileImage AS profile_image,
            ar.VerificationStatus AS verification_status,
            ar.CreatedAt AS created_at,
            (
                SELECT COUNT(*) FROM artist_follow af WHERE af.ArtistID = ar.ArtistID
            ) AS followers,
            (
                SELECT COUNT(*)
                FROM streamlog sl
                JOIN track t ON t.TrackID = sl.Track_TrackID
                JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
                WHERE aa.Artist_ArtistID = ar.ArtistID
            ) AS total_streams
        FROM artist ar
        WHERE ar.ArtistID = %s
        """,
        (artist_id,),
    )
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    artist["profile_image_url"] = resolve_image_url(
        "artist_profile",
        filename=artist.get("profile_image"),
        stems=(f"artist_{artist_id}", str(artist_id)),
    )
    artist["header_image_url"] = resolve_image_url(
        "artist_header",
        stems=(f"artist_{artist_id}", str(artist_id)),
    )

    social_links = fetch_all(
        "SELECT Platform AS platform, URL AS url FROM artistsocial WHERE Artist_ArtistID = %s ORDER BY Platform",
        (artist_id,),
    )

    labels = fetch_all(
        """
        SELECT
            rl.Name AS label_name,
            al.ContractStartDate AS contract_start_date,
            al.ContractEndDate AS contract_end_date
        FROM artistlabel al
        JOIN recordlabel rl ON rl.LabelID = al.RecordLabel_LabelID
        WHERE al.Artist_ArtistID = %s
        ORDER BY al.ContractStartDate DESC
        """,
        (artist_id,),
    )

    albums = fetch_all(
        """
        SELECT
            al.AlbumID AS album_id,
            al.Title AS title,
            al.ReleaseDate AS release_date,
            al.AlbumType AS album_type,
            al.CoverImage AS cover_image,
            COUNT(DISTINCT t.TrackID) AS tracks_count,
            GROUP_CONCAT(DISTINCT tg.TagName ORDER BY tg.TagName SEPARATOR ', ') AS tags
        FROM artistalbum aa
        JOIN album al ON al.AlbumID = aa.Album_AlbumID
        LEFT JOIN track t ON t.Album_AlbumID = al.AlbumID
        LEFT JOIN albumtag atg ON atg.Album_AlbumID = al.AlbumID
        LEFT JOIN tag tg ON tg.TagID = atg.Tag_TagID
        WHERE aa.Artist_ArtistID = %s
        GROUP BY al.AlbumID, al.Title, al.ReleaseDate, al.AlbumType, al.CoverImage
        ORDER BY al.ReleaseDate DESC
        """,
        (artist_id,),
    )
    for row in albums:
        album_id = row["album_id"]
        row["album_cover_url"] = resolve_image_url(
            "album_cover",
            filename=row.get("cover_image"),
            stems=(f"album_{album_id}", str(album_id)),
        )

    tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Duration AS duration,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams,
            GROUP_CONCAT(DISTINCT tg.TagName ORDER BY tg.TagName SEPARATOR ', ') AS tags
        FROM artistalbum aa
        JOIN album al ON al.AlbumID = aa.Album_AlbumID
        JOIN track t ON t.Album_AlbumID = al.AlbumID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        LEFT JOIN tracktag tt ON tt.Track_TrackID = t.TrackID
        LEFT JOIN tag tg ON tg.TagID = tt.Tag_TagID
        WHERE aa.Artist_ArtistID = %s
        GROUP BY t.TrackID, t.Title, t.Duration, t.Album_AlbumID, al.Title, al.CoverImage
        ORDER BY total_streams DESC, t.Title ASC
        """,
        (artist_id,),
    )
    tracks = [_track_assets(row) for row in tracks]
    upcoming_shows = fetch_all(
        """
        SELECT
            s.ShowID AS show_id,
            s.Title AS title,
            s.ShowDate AS show_date,
            s.ShowTime AS show_time,
            s.VenuName AS venue_name,
            s.VenueCity AS venue_city,
            s.VenueCountry AS venue_country,
            s.Status AS status,
            SUM(CASE WHEN COALESCE(t.Status, 'Booked') <> 'Cancelled' THEN 1 ELSE 0 END) AS booked_tickets
        FROM `show` s
        LEFT JOIN ticket t ON t.Show_ShowID = s.ShowID
        WHERE s.Artist_ArtistID = %s
        GROUP BY s.ShowID, s.Title, s.ShowDate, s.ShowTime, s.VenuName, s.VenueCity, s.VenueCountry, s.Status
        ORDER BY s.ShowDate ASC, s.ShowTime ASC
        """,
        (artist_id,),
    )
    artist["is_following"] = False
    if actor.get("user_id") is not None:
        artist["is_following"] = bool(
            fetch_one(
                "SELECT 1 AS yes FROM artist_follow WHERE UserID = %s AND ArtistID = %s",
                (actor["user_id"], artist_id),
            )
        )
    return {
        "artist": artist,
        "social_links": social_links,
        "labels": labels,
        "albums": albums,
        "tracks": tracks,
        "upcoming_shows": upcoming_shows,
    }


@app.get("/api/shows/{show_id}")
def show_details(show_id: int) -> dict[str, Any]:
    show = fetch_one(
        """
        SELECT
            s.ShowID AS show_id,
            s.Title AS title,
            s.Description AS description,
            s.ShowDate AS show_date,
            s.ShowTime AS show_time,
            s.VenuName AS venue_name,
            s.VenueCity AS venue_city,
            s.VenueCountry AS venue_country,
            s.Status AS status,
            s.Artist_ArtistID AS artist_id,
            a.StageName AS artist_name,
            SUM(CASE WHEN COALESCE(t.Status, 'Booked') <> 'Cancelled' THEN 1 ELSE 0 END) AS booked_tickets
        FROM `show` s
        JOIN artist a ON a.ArtistID = s.Artist_ArtistID
        LEFT JOIN ticket t ON t.Show_ShowID = s.ShowID
        WHERE s.ShowID = %s
        GROUP BY s.ShowID, s.Title, s.Description, s.ShowDate, s.ShowTime, s.VenuName, s.VenueCity, s.VenueCountry,
                 s.Status, s.Artist_ArtistID, a.StageName
        """,
        (show_id,),
    )
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    show["poster_image_url"] = resolve_image_url(
        "show_poster",
        stems=(f"show_{show_id}", str(show_id)),
    )
    return show


@app.post("/api/shows/{show_id}/book")
def book_ticket(show_id: int, payload: TicketBookingPayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    show = fetch_one(
        "SELECT ShowID AS show_id, Status AS status FROM `show` WHERE ShowID = %s",
        (show_id,),
    )
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    if (show.get("status") or "").lower() == "cancelled":
        raise HTTPException(status_code=400, detail="This show has been cancelled")

    category_prices = {
        "VIP": 1500.0,
        "Standard": 300.0,
        "Economy": 180.0,
    }
    price = category_prices.get(payload.seat_category, 300.0)

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.callproc(
                    "BookTicketWithValidation",
                    (
                        actor["user_id"],
                        show_id,
                        price,
                        payload.seat_section,
                        payload.seat_row,
                        payload.seat_number,
                        payload.seat_category,
                    ),
                )
                for result in cursor.stored_results():
                    result_data = result.fetchall()
                conn.commit()
    except mysql.connector.Error as exc:
        err_msg = str(exc)
        if "already booked" in err_msg.lower():
            raise HTTPException(status_code=400, detail="Seat already booked for this show") from exc
        _mysql_error(exc)

    return {"message": "Ticket booked", "ticket_id": cursor.lastrowid, "price": price}


@app.post("/api/tickets/{ticket_id}/cancel")
def cancel_ticket(ticket_id: int, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        changed = execute(
            """
            UPDATE ticket
            SET Status = 'Cancelled'
            WHERE TicketID = %s AND Users_UserID = %s
            """,
            (ticket_id, actor["user_id"]),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if changed == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket cancelled"}


@app.post("/api/follow/user")
def follow_user(payload: FollowUserPayload, request: Request) -> dict[str, str]:
    actor = _require_listener_actor(request)
    try:
        execute(
            """
            INSERT INTO user_follow (FollowerUserID, FollowedUserID, CreatedAt)
            VALUES (%s, %s, NOW())
            """,
            (actor["user_id"], payload.followed_user_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Followed user"}


@app.delete("/api/follow/user/{followed_user_id}")
def unfollow_user(followed_user_id: int, request: Request) -> dict[str, str]:
    actor = _require_listener_actor(request)
    try:
        removed = execute(
            "DELETE FROM user_follow WHERE FollowerUserID = %s AND FollowedUserID = %s",
            (actor["user_id"], followed_user_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if removed == 0:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "Unfollowed user"}


@app.post("/api/follow/artist")
def follow_artist(payload: FollowArtistPayload, request: Request) -> dict[str, str]:
    actor = _require_listener_actor(request)
    try:
        execute(
            """
            INSERT INTO artist_follow (UserID, ArtistID, CreatedAt)
            VALUES (%s, %s, NOW())
            """,
            (actor["user_id"], payload.artist_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Followed artist"}


@app.delete("/api/follow/artist/{artist_id}")
def unfollow_artist(artist_id: int, request: Request) -> dict[str, str]:
    actor = _require_listener_actor(request)
    try:
        removed = execute(
            "DELETE FROM artist_follow WHERE UserID = %s AND ArtistID = %s",
            (actor["user_id"], artist_id),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if removed == 0:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "Unfollowed artist"}


@app.post("/api/streams/start")
def start_stream(payload: StreamStartPayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.callproc(
                    "RecordStreamWithRoyaltyUpdate",
                    (
                        actor["user_id"],
                        payload.track_id,
                        payload.device_type,
                        payload.country,
                    ),
                )
                for result in cursor.stored_results():
                    result.fetchall()
                stream_id = cursor.lastrowid
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Stream started", "stream_id": stream_id}


@app.post("/api/streams/end")
def end_stream(payload: StreamEndPayload, request: Request) -> dict[str, Any]:
    actor = _require_listener_actor(request)
    skipped_at_value = payload.skipped_at if payload.skipped_at is not None else None
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(
                    "EndStreamEvent",
                    (payload.stream_id, actor["user_id"], 1 if payload.completed else 0, skipped_at_value),
                )
                conn.commit()
                row_count = cursor.rowcount
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if row_count == 0:
        raise HTTPException(status_code=404, detail="Stream record not found")
    return {"message": "Stream ended", "stream_id": payload.stream_id}


@app.get("/api/users/{user_id}/profile")
def user_profile(user_id: int, request: Request) -> dict[str, Any]:
    actor = _get_actor(request)
    user = fetch_one(
        """
        SELECT
            u.UserID AS user_id,
            u.FirstName AS first_name,
            u.Last_Name AS last_name,
            u.Username AS username,
            u.Email AS email,
            u.Country AS country,
            u.ProfileImage AS profile_image,
            u.CreatedAt AS created_at,
            p.PlanName AS plan_name,
            s.Status AS subscription_status,
            (
                SELECT COUNT(*) FROM user_follow uf WHERE uf.FollowedUserID = u.UserID
            ) AS followers,
            (
                SELECT COUNT(*) FROM user_follow uf WHERE uf.FollowerUserID = u.UserID
            ) AS following,
            (
                SELECT COUNT(*) FROM playlist pl WHERE pl.Users_UserID = u.UserID
            ) AS playlists,
            (
                SELECT COUNT(*) FROM streamlog sl WHERE sl.Users_UserID = u.UserID
            ) AS total_stream_events,
            (
                SELECT COUNT(*) FROM ticket tk WHERE tk.Users_UserID = u.UserID
            ) AS tickets_booked
        FROM users u
        LEFT JOIN subscription s ON s.Users_UserID = u.UserID
        LEFT JOIN plan p ON p.PlanID = s.Plan_PlanID
        WHERE u.UserID = %s
        """,
        (user_id,),
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id_value = user["user_id"]
    user["profile_image_url"] = resolve_image_url(
        "user_profile",
        filename=user.get("profile_image"),
        stems=(f"user_{user_id_value}", str(user_id_value)),
    )

    playlists = fetch_all(
        """
        SELECT
            pl.PlaylistID AS playlist_id,
            pl.Name AS name,
            pl.Description AS description,
            pl.IsPublic AS is_public,
            COUNT(pt.Track_TrackID) AS tracks_count
        FROM playlist pl
        LEFT JOIN playlisttrack pt ON pt.Playlist_PlaylistID = pl.PlaylistID
        WHERE pl.Users_UserID = %s
        GROUP BY pl.PlaylistID, pl.Name, pl.Description, pl.IsPublic
        ORDER BY pl.CreatedAt DESC
        """,
        (user_id,),
    )

    recent_streams = fetch_all(
        """
        SELECT
            sl.StreamID AS stream_id,
            sl.StartTime AS start_time,
            sl.EndTime AS end_time,
            sl.StreamDuration AS duration,
            sl.WasCompleted AS was_completed,
            t.TrackID AS track_id,
            t.Title AS track_title,
            a.CoverImage AS cover_image
        FROM streamlog sl
        JOIN track t ON t.TrackID = sl.Track_TrackID
        LEFT JOIN album a ON a.AlbumID = t.Album_AlbumID
        WHERE sl.Users_UserID = %s
        ORDER BY sl.StartTime DESC
        LIMIT 12
        """,
        (user_id,),
    )
    recent_streams = [_track_assets(row) for row in recent_streams]
    is_own_profile = actor.get("actor_type") == "listener" and actor.get("user_id") == user_id
    settings: dict[str, Any] | None = None
    tickets: list[dict[str, Any]] = []
    if is_own_profile:
        settings = my_settings(request)
        tickets = fetch_all(
            """
            SELECT
                tk.TicketID AS ticket_id,
                tk.Price AS price,
                tk.PurchaseDate AS purchase_date,
                CASE
                    WHEN COALESCE(tk.Status, 'Booked') = 'Cancelled' OR COALESCE(s.Status, 'Scheduled') = 'Cancelled'
                    THEN 'Cancelled'
                    ELSE COALESCE(tk.Status, 'Booked')
                END AS status,
                tk.SeatSection AS seat_section,
                tk.SeatRow AS seat_row,
                tk.SeatNumber AS seat_number,
                tk.SeatCategory AS seat_category,
                s.ShowID AS show_id,
                s.Title AS show_title,
                s.ShowDate AS show_date,
                s.ShowTime AS show_time,
                s.Status AS show_status,
                a.ArtistID AS artist_id,
                a.StageName AS artist_name
            FROM ticket tk
            JOIN `show` s ON s.ShowID = tk.Show_ShowID
            JOIN artist a ON a.ArtistID = s.Artist_ArtistID
            WHERE tk.Users_UserID = %s
            ORDER BY tk.PurchaseDate DESC
            """,
            (user_id,),
        )
    return {
        "user": user,
        "playlists": playlists,
        "recent_streams": recent_streams,
        "is_own_profile": is_own_profile,
        "settings": settings,
        "tickets": tickets,
    }


@app.get("/api/artist/me/dashboard")
def my_artist_dashboard(request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    return _artist_dashboard_data(actor["artist_id"])


@app.get("/api/artist/me/catalog")
def my_artist_catalog(request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    artist_id = actor["artist_id"]
    albums = fetch_all(
        """
        SELECT
            al.AlbumID AS album_id,
            al.Title AS title,
            al.ReleaseDate AS release_date,
            al.Language AS language,
            al.AlbumType AS album_type,
            al.CoverImage AS cover_image,
            COUNT(t.TrackID) AS tracks_count
        FROM artistalbum aa
        JOIN album al ON al.AlbumID = aa.Album_AlbumID
        LEFT JOIN track t ON t.Album_AlbumID = al.AlbumID
        WHERE aa.Artist_ArtistID = %s
        GROUP BY al.AlbumID, al.Title, al.ReleaseDate, al.Language, al.AlbumType, al.CoverImage
        ORDER BY al.ReleaseDate DESC
        """,
        (artist_id,),
    )
    for row in albums:
        album_id = row["album_id"]
        row["album_cover_url"] = resolve_image_url(
            "album_cover",
            filename=row.get("cover_image"),
            stems=(f"album_{album_id}", str(album_id)),
        )
    tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Duration AS duration,
            t.Album_AlbumID AS album_id,
            al.Title AS album_title,
            al.CoverImage AS cover_image,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM artistalbum aa
        JOIN track t ON t.Album_AlbumID = aa.Album_AlbumID
        LEFT JOIN album al ON al.AlbumID = t.Album_AlbumID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        WHERE aa.Artist_ArtistID = %s
        GROUP BY t.TrackID, t.Title, t.Duration, t.Album_AlbumID, al.Title, al.CoverImage
        ORDER BY t.ReleaseDate DESC
        """,
        (artist_id,),
    )
    tracks = [_track_assets(row) for row in tracks]
    shows = fetch_all(
        """
        SELECT
            s.ShowID AS show_id,
            s.Title AS title,
            s.ShowDate AS show_date,
            s.ShowTime AS show_time,
            s.VenuName AS venue_name,
            s.VenueCity AS venue_city,
            s.VenueCountry AS venue_country,
            s.Status AS status,
            SUM(CASE WHEN COALESCE(t.Status, 'Booked') <> 'Cancelled' THEN 1 ELSE 0 END) AS booked_tickets
        FROM `show` s
        LEFT JOIN ticket t ON t.Show_ShowID = s.ShowID
        WHERE s.Artist_ArtistID = %s
        GROUP BY s.ShowID, s.Title, s.ShowDate, s.ShowTime, s.VenuName, s.VenueCity, s.VenueCountry, s.Status
        ORDER BY s.ShowDate ASC, s.ShowTime ASC
        """,
        (artist_id,),
    )
    return {"albums": albums, "tracks": tracks, "shows": shows}


@app.post("/api/artist/me/albums")
def create_artist_album(payload: ArtistAlbumCreatePayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO album (Title, ReleaseDate, Language, AlbumType, CoverImage)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        payload.title,
                        payload.release_date,
                        payload.language,
                        payload.album_type,
                        payload.cover_image or "",
                    ),
                )
                album_id = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO artistalbum (Album_AlbumID, Artist_ArtistID)
                    VALUES (%s, %s)
                    """,
                    (album_id, actor["artist_id"]),
                )
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Album created", "album_id": album_id}


@app.post("/api/artist/me/albums/{album_id}/tags")
def set_album_tags(album_id: int, payload: AlbumTagsPayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    album = fetch_one(
        """
        SELECT aa.Album_AlbumID AS album_id
        FROM artistalbum aa
        WHERE aa.Album_AlbumID = %s AND aa.Artist_ArtistID = %s
        """,
        (album_id, actor["artist_id"]),
    )
    if not album:
        raise HTTPException(status_code=403, detail="Album does not belong to this artist")
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                resolved_tag_ids = _resolve_tag_ids(cursor, payload.tag_ids, payload.tag_names)
                cursor.execute("DELETE FROM albumtag WHERE Album_AlbumID = %s", (album_id,))
                for tag_id in resolved_tag_ids:
                    cursor.execute(
                        """
                        INSERT IGNORE INTO albumtag (Album_AlbumID, Tag_TagID)
                        VALUES (%s, %s)
                        """,
                        (album_id, tag_id),
                    )
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Album tags updated"}


@app.post("/api/artist/me/tracks")
def create_artist_track(payload: ArtistTrackCreatePayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    if payload.album_id is not None:
        album = fetch_one(
            """
            SELECT aa.Album_AlbumID AS album_id
            FROM artistalbum aa
            WHERE aa.Album_AlbumID = %s AND aa.Artist_ArtistID = %s
            """,
            (payload.album_id, actor["artist_id"]),
        )
        if not album:
            raise HTTPException(status_code=403, detail="Album does not belong to this artist")
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                resolved_tag_ids = _resolve_tag_ids(cursor, payload.tag_ids, payload.tag_names)
                cursor.execute(
                    """
                    INSERT INTO track (Title, Duration, Language, Lyrics, ReleaseDate, BPM, Album_AlbumID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        payload.title,
                        payload.duration,
                        payload.language,
                        payload.lyrics,
                        payload.release_date,
                        payload.bpm,
                        payload.album_id,
                    ),
                )
                track_id = cursor.lastrowid
                for tag_id in resolved_tag_ids:
                    cursor.execute(
                        """
                        INSERT IGNORE INTO tracktag (Track_TrackID, Tag_TagID)
                        VALUES (%s, %s)
                        """,
                        (track_id, tag_id),
                    )
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Track created", "track_id": track_id}


@app.get("/api/tracks/{track_id}/credits")
def list_track_credits(track_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            c.CreditID AS credit_id,
            c.PersonName AS person_name,
            c.Role AS role,
            c.EntityType AS entity_type
        FROM credits c
        WHERE c.Track_TrackID = %s
        ORDER BY c.CreditID DESC
        """,
        (track_id,),
    )


@app.post("/api/artist/me/tracks/{track_id}/credits")
def add_track_credit(track_id: int, payload: TrackCreditPayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    allowed = fetch_one(
        """
        SELECT t.TrackID AS track_id
        FROM track t
        JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
        WHERE t.TrackID = %s AND aa.Artist_ArtistID = %s
        """,
        (track_id, actor["artist_id"]),
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Track does not belong to this artist")
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO credits (PersonName, Role, EntityType, Track_TrackID)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (payload.person_name, payload.role, payload.entity_type, track_id),
                )
                conn.commit()
                credit_id = cursor.lastrowid
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Credit added", "credit_id": credit_id}


@app.post("/api/artist/me/shows")
def create_artist_show(payload: ArtistShowCreatePayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO `show`
                    (Title, Description, ShowDate, ShowTime, VenuName, VenueCity, VenueCountry, Status, Artist_ArtistID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        payload.title,
                        payload.description,
                        payload.show_date,
                        payload.show_time,
                        payload.venue_name,
                        payload.venue_city,
                        payload.venue_country,
                        payload.status,
                        actor["artist_id"],
                    ),
                )
                conn.commit()
                show_id = cursor.lastrowid
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Show created", "show_id": show_id}


@app.patch("/api/artist/me/shows/{show_id}")
def update_artist_show(show_id: int, payload: ArtistShowUpdatePayload, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    show = fetch_one(
        "SELECT ShowID AS show_id FROM `show` WHERE ShowID = %s AND Artist_ArtistID = %s",
        (show_id, actor["artist_id"]),
    )
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    current = fetch_one(
        """
        SELECT Title, Description, ShowDate, ShowTime, VenuName, VenueCity, VenueCountry, Status
        FROM `show`
        WHERE ShowID = %s
        """,
        (show_id,),
    )
    try:
        execute(
            """
            UPDATE `show`
            SET Title = %s,
                Description = %s,
                ShowDate = %s,
                ShowTime = %s,
                VenuName = %s,
                VenueCity = %s,
                VenueCountry = %s,
                Status = %s
            WHERE ShowID = %s
            """,
            (
                payload.title if payload.title is not None else current["Title"],
                payload.description if payload.description is not None else current["Description"],
                payload.show_date if payload.show_date is not None else current["ShowDate"],
                payload.show_time if payload.show_time is not None else current["ShowTime"],
                payload.venue_name if payload.venue_name is not None else current["VenuName"],
                payload.venue_city if payload.venue_city is not None else current["VenueCity"],
                payload.venue_country if payload.venue_country is not None else current["VenueCountry"],
                payload.status if payload.status is not None else current["Status"],
                show_id,
            ),
        )
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    return {"message": "Show updated"}


@app.delete("/api/artist/me/shows/{show_id}")
def cancel_artist_show(show_id: int, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    UPDATE `show`
                    SET Status = 'Cancelled'
                    WHERE ShowID = %s AND Artist_ArtistID = %s
                    """,
                    (show_id, actor["artist_id"]),
                )
                changed = cursor.rowcount
                if changed > 0:
                    cursor.execute(
                        """
                        UPDATE ticket
                        SET Status = 'Cancelled'
                        WHERE Show_ShowID = %s
                          AND COALESCE(Status, 'Booked') <> 'Cancelled'
                        """,
                        (show_id,),
                    )
                conn.commit()
    except mysql.connector.Error as exc:
        _mysql_error(exc)
    if changed == 0:
        raise HTTPException(status_code=404, detail="Show not found")
    return {"message": "Show cancelled"}


def _artist_dashboard_data(artist_id: int) -> dict[str, Any]:
    artist = fetch_one(
        """
        SELECT
            a.ArtistID AS artist_id,
            a.StageName AS stage_name,
            (
                SELECT COUNT(*) FROM artist_follow af WHERE af.ArtistID = a.ArtistID
            ) AS followers,
            (
                SELECT COUNT(*)
                FROM streamlog sl
                JOIN track t ON t.TrackID = sl.Track_TrackID
                JOIN artistalbum aa ON aa.Album_AlbumID = t.Album_AlbumID
                WHERE aa.Artist_ArtistID = a.ArtistID
            ) AS total_streams,
            (
                SELECT COALESCE(SUM(r.TotalAmount), 0)
                FROM royalty r
                WHERE r.Artist_ArtistID = a.ArtistID
            ) AS total_royalty_amount
        FROM artist a
        WHERE a.ArtistID = %s
        """,
        (artist_id,),
    )
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    artist_id_value = artist["artist_id"]
    artist["profile_image_url"] = resolve_image_url(
        "artist_profile",
        stems=(f"artist_{artist_id_value}", str(artist_id_value)),
    )

    top_tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            a.CoverImage AS cover_image,
            COUNT(sl.StreamID) AS total_streams,
            COALESCE(SUM(r.TotalAmount), 0) AS royalty_total
        FROM artistalbum aa
        JOIN track t ON t.Album_AlbumID = aa.Album_AlbumID
        LEFT JOIN album a ON a.AlbumID = t.Album_AlbumID
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        LEFT JOIN royalty r ON r.Track_TrackID = t.TrackID AND r.Artist_ArtistID = aa.Artist_ArtistID
        WHERE aa.Artist_ArtistID = %s
        GROUP BY t.TrackID, t.Title, a.CoverImage
        ORDER BY total_streams DESC, title ASC
        LIMIT 10
        """,
        (artist_id,),
    )
    top_tracks = [_track_assets(row) for row in top_tracks]
    royalties = fetch_all(
        """
        SELECT
            r.RoyaltyID AS royalty_id,
            t.Title AS track_title,
            r.StreamCount AS stream_count,
            r.TotalAmount AS total_amount,
            r.Currency AS currency,
            r.PaymentStatus AS payment_status,
            r.PeriodStart AS period_start,
            r.PeriodEnd AS period_end,
            r.RoyaltyRate AS royalty_rate
        FROM royalty r
        JOIN track t ON t.TrackID = r.Track_TrackID
        WHERE r.Artist_ArtistID = %s
        ORDER BY r.PeriodEnd DESC
        """,
        (artist_id,),
    )
    royalty_overview = fetch_one(
        """
        SELECT
            COALESCE(AVG(r.RoyaltyRate), 0) AS avg_royalty_rate,
            COALESCE(SUM(r.TotalAmount), 0) AS total_royalty_amount,
            COALESCE(SUM(r.StreamCount), 0) AS total_stream_count,
            COUNT(*) AS royalty_rows
        FROM royalty r
        WHERE r.Artist_ArtistID = %s
        """,
        (artist_id,),
    )
    labels = fetch_all(
        """
        SELECT
            rl.LabelID AS label_id,
            rl.Name AS label_name,
            al.ContractStartDate AS contract_start_date,
            al.ContractEndDate AS contract_end_date,
            rl.ContactEmail AS contact_email,
            rl.Country AS country,
            CASE
                WHEN al.ContractEndDate IS NULL OR al.ContractEndDate >= CURDATE() THEN 1
                ELSE 0
            END AS is_active,
            AVG(
                CASE
                    WHEN r.RoyaltyRate IS NOT NULL
                     AND (al.ContractStartDate IS NULL OR r.PeriodStart >= al.ContractStartDate)
                     AND (al.ContractEndDate IS NULL OR r.PeriodEnd <= al.ContractEndDate)
                    THEN r.RoyaltyRate
                    ELSE NULL
                END
            ) AS avg_royalty_rate,
            COALESCE(
                SUM(
                    CASE
                        WHEN (al.ContractStartDate IS NULL OR r.PeriodStart >= al.ContractStartDate)
                         AND (al.ContractEndDate IS NULL OR r.PeriodEnd <= al.ContractEndDate)
                        THEN r.TotalAmount
                        ELSE 0
                    END
                ),
                0
            ) AS total_royalty_amount
        FROM artistlabel al
        JOIN recordlabel rl ON rl.LabelID = al.RecordLabel_LabelID
        LEFT JOIN royalty r ON r.Artist_ArtistID = al.Artist_ArtistID
        WHERE al.Artist_ArtistID = %s
        GROUP BY rl.LabelID, rl.Name, al.ContractStartDate, al.ContractEndDate, rl.ContactEmail, rl.Country
        ORDER BY is_active DESC, al.ContractStartDate DESC
        """,
        (artist_id,),
    )
    for row in labels:
        row["is_active"] = bool(row.get("is_active"))
    active_label = next((row for row in labels if row.get("is_active")), None)
    shows = fetch_all(
        """
        SELECT
            s.ShowID AS show_id,
            s.Title AS title,
            s.ShowDate AS show_date,
            s.ShowTime AS show_time,
            s.VenuName AS venue_name,
            SUM(CASE WHEN COALESCE(t.Status, 'Booked') <> 'Cancelled' THEN 1 ELSE 0 END) AS tickets_booked
        FROM `show` s
        LEFT JOIN ticket t ON t.Show_ShowID = s.ShowID
        WHERE s.Artist_ArtistID = %s
        GROUP BY s.ShowID, s.Title, s.ShowDate, s.ShowTime, s.VenuName
        ORDER BY s.ShowDate ASC
        """,
        (artist_id,),
    )
    return {
        "artist": artist,
        "top_tracks": top_tracks,
        "royalties": royalties,
        "royalty_overview": royalty_overview,
        "labels": labels,
        "active_label": active_label,
        "shows": shows,
    }


@app.get("/api/artists/{artist_id}/dashboard")
def artist_dashboard(artist_id: int, request: Request) -> dict[str, Any]:
    actor = _require_artist_actor(request)
    if actor["artist_id"] != artist_id:
        raise HTTPException(status_code=403, detail="You can only access your own artist dashboard")
    return _artist_dashboard_data(artist_id)


@app.get("/api/albums/{album_id}")
def album_details(album_id: int, request: Request) -> dict[str, Any]:
    album = fetch_one(
        """
        SELECT
            al.AlbumID AS album_id,
            al.Title AS title,
            al.ReleaseDate AS release_date,
            al.Language AS language,
            al.AlbumType AS album_type,
            al.CoverImage AS cover_image,
            ar.ArtistID AS artist_id,
            ar.StageName AS artist_name,
            ar.ProfileImage AS artist_profile_image,
            GetAlbumTrackCount(al.AlbumID) AS tracks_count,
            GetAlbumDuration(al.AlbumID) AS total_duration,
            GROUP_CONCAT(DISTINCT tg.TagName ORDER BY tg.TagName SEPARATOR ', ') AS tags
        FROM album al
        JOIN artistalbum aa ON aa.Album_AlbumID = al.AlbumID
        JOIN artist ar ON ar.ArtistID = aa.Artist_ArtistID
        LEFT JOIN albumtag atg ON atg.Album_AlbumID = al.AlbumID
        LEFT JOIN tag tg ON tg.TagID = atg.Tag_TagID
        WHERE al.AlbumID = %s
        GROUP BY al.AlbumID, al.Title, al.ReleaseDate, al.Language, al.AlbumType, al.CoverImage,
                 ar.ArtistID, ar.StageName, ar.ProfileImage
        """,
        (album_id,),
    )
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    album_id_value = album["album_id"]
    album["album_cover_url"] = resolve_image_url(
        "album_cover",
        filename=album.get("cover_image"),
        stems=(f"album_{album_id_value}", str(album_id_value)),
    )
    artist_id = album.get("artist_id")
    if artist_id:
        album["artist_profile_url"] = resolve_image_url(
            "artist_profile",
            filename=album.get("artist_profile_image"),
            stems=(f"artist_{artist_id}", str(artist_id)),
        )

    tracks = fetch_all(
        """
        SELECT
            t.TrackID AS track_id,
            t.Title AS title,
            t.Duration AS duration,
            t.Language AS language,
            t.ReleaseDate AS release_date,
            COALESCE(COUNT(sl.StreamID), 0) AS total_streams
        FROM track t
        LEFT JOIN streamlog sl ON sl.Track_TrackID = t.TrackID
        WHERE t.Album_AlbumID = %s
        GROUP BY t.TrackID, t.Title, t.Duration, t.Language, t.ReleaseDate
        ORDER BY t.TrackID ASC
        """,
        (album_id,),
    )
    tracks = [_track_assets(row) for row in tracks]

    return {"album": album, "tracks": tracks}
