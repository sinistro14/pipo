from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class SkipList(Command):
    _bot: Groovy
    _ctx: Dctx

    async def execute(self) -> None:
        await self._bot.skip(self._ctx, skip_list=True)
