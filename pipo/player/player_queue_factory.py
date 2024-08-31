from pipo.config import settings
from pipo.player.music_queue.local.local_music_queue import LocalMusicQueue
from pipo.player.player_queue import PlayerQueue
from pipo.player.player_queue_type import QueueType


class PlayerQueueFactory:
    """Factory to generate music queue types.

    Factory able to generate different types of music queue.
    Available types in :class:`~pipo.player.music_queue.queue_type.QueueType`.
    """

    @staticmethod
    def get(queue_type: QueueType = QueueType.NONE) -> PlayerQueue:
        """Obtain requested music queue type.

        Parameters
        ----------
        queue_type : QueueType, optional
            Music queue type, by default QueueType.NONE, corresponding to default queue.

        Returns
        -------
        MusicQueue
            Generated music queue.
        """
        queues = {
            QueueType.LOCAL: LocalMusicQueue,
        }
        return queues.get(queue_type, queues.get(settings.player.queue.default))()
