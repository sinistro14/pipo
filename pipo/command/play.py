from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class Play(Command):
    _bot: Groovy
    _ctx: Dctx
    _query: str

    async def execute(self) -> None:
        self._ctx.kwargs["_query_"] = " ".join(self._query)
        await self._bot.play(self._ctx)
