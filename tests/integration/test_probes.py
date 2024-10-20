#!usr/bin/env python3
import pytest
import requests

from tests.conftest import Helpers
from pipo.probes import get_probe_server


@pytest.mark.integration
class TestHealthProbes:
    @pytest.fixture(scope="function", autouse=True)
    async def server_url(self):
        server = get_probe_server(Helpers.get_available_port())
        with server.run_in_thread():
            yield f"http://{server.config.host}:{server.config.port}"

    @pytest.mark.asyncio
    async def test_healthz(self, server_url):
        response = requests.get(f"{server_url}/healthz")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_readyz(self, server_url):
        response = requests.get(f"{server_url}/readyz")
        assert response.status_code == 200
