import psutil

from pipo.groovy import Groovy
from .command import Command

class Status(Command):

    def __init__(self, bot: Groovy, ctx) -> None:
        self._bot = bot
        self._ctx = ctx

    async def execute(self) -> None:
        await self._bot._moveMessage(self._ctx)
        await self._bot.send_message(
            f"Current State: {self._bot.currentState.name}\n"
            f"Queue Length: {self._bot._music_queue.getLength()}\n"
            f"CPU Usage: {psutil.cpu_percent()}\n"
            f"RAM Usage: {psutil.virtual_memory().percent}%\n"
            f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
            f"Temperature: {psutil.sensors_temperatures()['cpu_thermal'][0][1]} ºC"
        )
