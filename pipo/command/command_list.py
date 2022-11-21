from pipo.groovy import Groovy
from .command import Command

class CommandList(Command):

    def __init__(self, payload: str) -> None:
        self._payload = payload

    def __init__(self, bot: Groovy) -> None:
        self._bot = bot

    async def execute(self) -> None:
        await self._bot.send_message(
            "Command List: \n "
            " -join \n"
            " -play <query / url> \n"
            " -pause \n"
            " -resume \n"
            " -skip \n"
            " -stop \n"
            " -leave \n"
            " -playlist <url> \n"
            " -playlistshuffle <url> \n"
            " -skiplist \n"
            " -state \n"
            " -help"
        )
