#!usr/bin/env python3

import asyncio
import signal


class SignalManager:
    """Manage program signals."""

    @staticmethod
    async def __shutdown(signal, loop: asyncio.AbstractEventLoop) -> None:
        """Cancel all running async tasks.

        Cancel running asyncio tasks, except this one, so they can perform necessary
        cleanup, when cancelled, by processing an asyncio.CancelledError exception.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            Loop from where tasks should cancelled.
        """
        tasks = [
            task for task in asyncio.all_tasks() if task is not asyncio.current_task()
        ]

        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    @staticmethod
    def add_handlers(loop: asyncio.AbstractEventLoop) -> None:
        """Add signal handlers to manage program execution."""
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT]:
            loop.add_signal_handler(
                sig,
                lambda sig=sig: asyncio.create_task(
                    SignalManager.__shutdown(sig, loop)
                ),
            )
