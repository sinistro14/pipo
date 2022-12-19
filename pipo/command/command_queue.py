from concurrent.futures import Future, ThreadPoolExecutor

from pipo.command import Command


class CommandQueue:

    _command_executor: ThreadPoolExecutor

    def __init__(self, max_workers: int) -> None:
        self._command_executor = ThreadPoolExecutor(max_workers=max_workers)

    def add(self, command: Command) -> Future:
        return self._command_executor.submit(command.execute)

    def stop(self):
        self._command_executor.shutdown()
