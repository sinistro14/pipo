from pipo.groovy import Groovy
from .command import Command

class Play(Command):

    def __init__(self, bot: Groovy, ctx, query) -> None:
        self._bot = bot
        self._ctx = ctx
        self._query = query

    async def execute(self) -> None:
        self._ctx.kwargs["_query_"] = " ".join(self._query)
        await self._bot.play(self._ctx)
