from dataclasses import dataclass
from typing import List

from discord.ext.commands import Context as Dctx

from pipo.command.command import Command
from pipo.pipo import Pipo


@dataclass
class Play(Command):
    bot: Pipo
    ctx: Dctx
    query: List[str]
    shuffle: bool

    async def _execute(self) -> None:
        await self.bot.play(self.ctx, self.query, self.shuffle)
