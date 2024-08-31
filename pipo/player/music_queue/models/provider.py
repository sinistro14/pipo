"""Music Provider."""

try:
    # breaking change introduced in python 3.11
    from enum import StrEnum
except ImportError:  # pragma: no cover
    from enum import Enum  # pragma: no cover

    class StrEnum(str, Enum):  # pragma: no cover
        """String inherited Enum."""

        pass  # pragma: no cover


class Provider(StrEnum):
    """Provider types."""

    YOUTUBE = "youtube"
    YOUTUBE_QUERY = "youtube_query"
    SPOTIFY = "spotify"
