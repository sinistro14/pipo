from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.command.command import Command
from pipo.pipo import Pipo


@dataclass
class Leave(Command):
    """Command bot to leave server."""

    bot: Pipo
    ctx: Dctx

    async def _execute(self) -> None:
        await self.bot.leave(self.ctx)
