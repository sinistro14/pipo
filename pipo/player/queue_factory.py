from pipo.config import settings
from pipo.player.music_queue.local import LocalMusicQueue
from pipo.player.music_queue.remote.music_queue import music_queue
from pipo.player.queue import PlayerQueue, QueueType


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
            QueueType.LOCAL: LocalMusicQueue(),
            QueueType.REMOTE: music_queue,
        }
        return queues.get(queue_type, queues.get(settings.player.queue.default))
