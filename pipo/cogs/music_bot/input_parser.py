#!usr/bin/env python3
import argparse
from dataclasses import dataclass
from typing import Iterable, List, Optional

from pipo.config import settings


@dataclass
class PlayArguments:
    """Parsed play arguments."""

    shuffle: bool
    search: bool
    query: List[str]


class InputParser:
    """Parses music bot commands."""

    __parser: argparse.ArgumentParser

    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            settings.commands.search,
            dest="search",
            action="store_true",
            required=False,
        )
        parser.add_argument(
            settings.commands.shuffle,
            dest="shuffle",
            action="store_true",
            required=False,
        )
        parser.add_argument("query", nargs="*", default=[])
        self.__parser = parser

    def parse_play(self, args: Iterable[str]) -> Optional[PlayArguments]:
        """Parse play music command.

        Parameters
        ----------
        args : Iterable[str]
            List of arguments to parse.

        Returns
        -------
        Optional[PlayArguments]
            Parsed arguments, None in case of error.
        """
        try:
            args = self.__parser.parse_args(args)
        except argparse.ArgumentError:
            return None
        return PlayArguments(shuffle=args.shuffle, search=args.search, query=args.query)
