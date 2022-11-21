from pipo.groovy import Groovy
from .command import Command

class Reboot(Command):

    def __init__(self, bot: Groovy) -> None:
        self._bot = bot

    async def execute(self) -> None:
        await self._bot.reboot()
