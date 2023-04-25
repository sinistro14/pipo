from dataclasses import dataclass

import psutil
from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.command.command import Command


@dataclass
class Status(Command):
    bot: Groovy
    ctx: Dctx

    async def execute(self) -> None:
        await self.bot.move_message(self.ctx)
        await self.bot.send_message(
            f"Current State: {self.bot.current_state()}\n"
            f"Queue Length: {self.bot.queue_size()}\n"
            f"CPU Usage: {psutil.cpu_percent()}\n"
            f"RAM Usage: {psutil.virtual_memory().percent}%\n"
            f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
            f"Temperature: {psutil.sensors_temperatures()['cpu_thermal'][0][1]} ºC"
        )
