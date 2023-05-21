from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.pipo import Pipo
from pipo.command.command import Command


@dataclass
class SkipList(Command):
    bot: Pipo
    ctx: Dctx

    async def execute(self) -> None:
        await self.bot.skip(self.ctx, skip_list=True)
