from typing import List
from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.pipo import Pipo
from pipo.command.command import Command


@dataclass
class Play(Command):
    bot: Pipo
    ctx: Dctx
    query: List[str]
    shuffle: bool

    async def _execute(self) -> None:
        await self.bot.play(self.ctx, self.query, self.shuffle)
