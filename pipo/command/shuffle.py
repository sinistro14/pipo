from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.command import Command
from pipo.groovy import Groovy


@dataclass
class Shuffle(Command):
    bot: Groovy
    ctx: Dctx

    def execute(self) -> None:
        self.bot.shuffle()
