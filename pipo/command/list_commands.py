from dataclasses import dataclass

from pipo.pipo import Pipo
from pipo.config import settings
from pipo.command.command import Command


@dataclass
class ListCommands(Command):
    bot: Pipo

    async def _execute(self) -> None:
        await self.bot.send_message(
            f"""
            Command List: \n
             -help \n
             -join \n
             -leave \n
             -resume \n
             -play [{settings.command.commands.shuffle}] <query> | <music_url> | <playlist_url> \n
             -pause \n
             -shuffle \n
             -skip \n
             -stop
            """
        )
