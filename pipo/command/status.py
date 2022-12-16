from dataclasses import dataclass

import psutil
from discord.ext.commands import Context as Dctx

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class Status(Command):
    _bot: Groovy
    _ctx: Dctx

    async def execute(self) -> None:
        await self._bot._move_message(self._ctx)
        await self._bot.send_message(
            f"Current State: {self._bot.current_state()}\n"
            f"Queue Length: {self._bot.queue_size()}\n"
            f"CPU Usage: {psutil.cpu_percent()}\n"
            f"RAM Usage: {psutil.virtual_memory().percent}%\n"
            f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
            f"Temperature: {psutil.sensors_temperatures()['cpu_thermal'][0][1]} ºC"
        )
