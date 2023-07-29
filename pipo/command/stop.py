from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.command.command import Command
from pipo.pipo import Pipo


@dataclass
class Stop(Command):
    """Command to stop music and clear queue."""

    bot: Pipo
    ctx: Dctx

    async def _execute(self) -> None:
        await self.bot.stop(self.ctx)
