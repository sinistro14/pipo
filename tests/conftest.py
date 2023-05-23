import random as rand
import logging
import functools
from typing import Iterable

import pytest
from dynaconf import settings


class Helpers:
    @staticmethod
    def equal_iterables(iter_1: Iterable, iter_2: Iterable):
        return functools.reduce(
            lambda x, y: x and y,
            map(lambda p, q: p == q, iter_1, iter_2),
            True,
        )


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture(scope="session", autouse=True)
def random():
    rand.seed(0)


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="test")
    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
