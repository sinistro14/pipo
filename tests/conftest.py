import logging
import random as rand

import pytest
from dynaconf import settings

@pytest.fixture(scope="session", autouse=True)
def random():
    rand.seed(0)

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="test")
    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
