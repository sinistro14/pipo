from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.pipo import Pipo
from pipo.command.command import Command


@dataclass
class Leave(Command):
    bot: Pipo
    ctx: Dctx

    async def _execute(self) -> None:
        await self.bot.leave(self.ctx)
