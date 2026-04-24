from pathlib import Path
from typing import Iterable

from app.config import settings


MEDIA_ROOT = Path(settings.media_root)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a")

IMAGE_DIRS = {
    "user_profile": "users/profiles",
    "artist_profile": "artists/profiles",
    "artist_header": "artists/headers",
    "album_cover": "albums/covers",
    "track_cover": "tracks/covers",
    "show_poster": "shows/posters",
}

AUDIO_DIRS = {
    "track_audio": "tracks/audio",
}


def _safe_name(value: str | None) -> str | None:
    if not value:
        return None
    return Path(value).name.strip()


def _stem(value: str | None) -> str | None:
    cleaned = _safe_name(value)
    if not cleaned:
        return None
    return Path(cleaned).stem


def _public_url(rel_path: str) -> str:
    prefix = settings.media_url_prefix.rstrip("/")
    base = settings.backend_public_url.rstrip("/")
    return f"{base}{prefix}/{rel_path.replace('\\', '/')}"


def _check_candidates(directory: Path, file_names: Iterable[str]) -> str | None:
    for file_name in file_names:
        full_path = directory / file_name
        if full_path.exists() and full_path.is_file():
            rel = full_path.relative_to(MEDIA_ROOT)
            return _public_url(str(rel))
    return None


def resolve_image_url(
    kind: str,
    *,
    filename: str | None = None,
    stems: Iterable[str] = (),
    fallback_placeholder: str = "placeholders/image.svg",
) -> str:
    relative_dir = IMAGE_DIRS[kind]
    directory = MEDIA_ROOT / relative_dir

    explicit = _safe_name(filename)
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)

    explicit_stem = _stem(filename)
    all_stems = [s for s in [explicit_stem, *stems] if s]
    for stem in all_stems:
        for ext in IMAGE_EXTENSIONS:
            candidates.append(f"{stem}{ext}")

    found = _check_candidates(directory, candidates)
    if found:
        return found
    return _public_url(fallback_placeholder)


def resolve_track_audio_url(
    track_id: int,
    *,
    filename: str | None = None,
    fallback_placeholder: str = "placeholders/audio.svg",
) -> str:
    directory = MEDIA_ROOT / AUDIO_DIRS["track_audio"]

    explicit = _safe_name(filename)
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)

    for stem in (str(track_id), f"track_{track_id}"):
        for ext in AUDIO_EXTENSIONS:
            candidates.append(f"{stem}{ext}")

    found = _check_candidates(directory, candidates)
    if found:
        return found
    return _public_url(fallback_placeholder)
