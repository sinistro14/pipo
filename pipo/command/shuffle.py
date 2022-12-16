from dataclasses import dataclass

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class Shuffle(Command):
    _bot: Groovy

    async def execute(self) -> None:
        await self._bot.shuffle()
