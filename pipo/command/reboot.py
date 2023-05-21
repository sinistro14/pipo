from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.pipo import Pipo
from pipo.command.command import Command


@dataclass
class Reboot(Command):
    bot: Pipo
    ctx: Dctx

    async def execute(self) -> None:
        await self.bot.reboot(self.ctx)
