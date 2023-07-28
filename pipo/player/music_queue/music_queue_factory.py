from pipo.config import settings
from pipo.player.music_queue.local_music_queue import LocalMusicQueue
from pipo.player.music_queue.music_queue import MusicQueue
from pipo.player.music_queue.queue_type import QueueType


class MusicQueueFactory:

    @staticmethod
    def get(queue_type: QueueType) -> MusicQueue:
        queues = {
            QueueType.LOCAL: LocalMusicQueue,
        }
        return queues.get(queue_type, queues.get(settings.player.queue.default))()
