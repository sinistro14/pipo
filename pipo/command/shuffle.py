from dataclasses import dataclass

from discord.ext.commands import Context as Dctx

from pipo.groovy import Groovy
from pipo.command.command import Command


@dataclass
class Shuffle(Command):
    bot: Groovy
    ctx: Dctx

    async def execute(self) -> None:
        await self.bot.shuffle(self.ctx)
