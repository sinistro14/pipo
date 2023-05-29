#!usr/bin/env python3

import asyncio

import pytest


class TestPytest:
    def test_pytest(self):
        assert True

    @pytest.mark.asyncio
    async def test_pytest_asyncio(self):
        await asyncio.sleep(0.5)
