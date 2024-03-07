from typing import Any, Iterable, Optional

from pipo.config import settings
from pipo.player.audio_source.source_pair import SourcePair
from pipo.player.music_queue.music_queue import MusicQueue

class RabbitMQMusicQueue(MusicQueue):
    """Cloud hosted message broker as music queue.
    """

    def __init__(self) -> None:
        pass

    def _add(self, music: str) -> None:
        """Add item to queue."""
        pass

    def _get(self) -> Optional[str]:
        """Get queue item."""
        pass

    def _submit_fetch(self, sources: Iterable[SourcePair]) -> None:
        pass

    def _clear(self) -> None:
        """Clear queue."""
        pass

    def get_all(self) -> Any:
        """Get enqueued music."""
        pass

    def fetch_queue_size(self) -> int:
        """Fetch queue size."""
        pass

    def audio_queue_size(self) -> int:
        """Audio queue queue size."""
        pass