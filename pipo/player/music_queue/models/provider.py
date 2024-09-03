"""Music Provider."""
from enum import StrEnum


class Provider(StrEnum):
    """Provider types."""

    YOUTUBE = "youtube"
    YOUTUBE_QUERY = "youtube_query"
    SPOTIFY = "spotify"
