from pipo.groovy import Groovy
from .command import Command

class PlayList(Command):

    def __init__(self, bot: Groovy, ctx, query, shuffle) -> None:
        self._bot = bot
        self._ctx = ctx
        self._query = query
        self._shuffle = shuffle

    async def execute(self) -> None:
        self._ctx.kwargs["_query_"] = " ".join(self._query)
        await self._bot.playList(self._ctx, shuffle=self._shuffle)
