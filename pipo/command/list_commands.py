from dataclasses import dataclass

from pipo.pipo import Pipo
from pipo.config import settings
from pipo.command.command import Command


@dataclass
class ListCommands(Command):
    bot: Pipo

    async def execute(self) -> None:
        await self.bot.send_message(
            f"""
            Command List: \n
             -join \n
             -play [{settings.command.commands.shuffle}] <query> | <music_url> | <playlist_url> \n
             -pause \n
             -resume \n
             -skip \n
             -stop \n
             -leave \n
             -state \n
             -help
            """
        )
