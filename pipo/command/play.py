from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.command.command import Command


@dataclass
class Play(Command):
    bot: Groovy
    ctx: Dctx
    query: str

    async def execute(self) -> None:
        self.ctx.kwargs["_query_"] = " ".join(self.query)
        await self.bot.play(self._ctx)
