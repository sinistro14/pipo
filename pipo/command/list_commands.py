from dataclasses import dataclass

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class ListCommands(Command):
    bot: Groovy

    async def execute(self) -> None:
        await self.bot.send_message(
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
