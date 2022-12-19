from dataclasses import dataclass

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class Shuffle(Command):
    bot: Groovy

    async def execute(self) -> None:
        await self.bot.shuffle()
