from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.pipo import Pipo
from pipo.command.command import Command


@dataclass
class Resume(Command):
    bot: Pipo
    ctx: Dctx

    async def execute(self) -> None:
        await self.bot.resume(self.ctx)
