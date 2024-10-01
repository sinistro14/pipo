import pytest

import pipo.player
import tests.constants


class TestPlayer:
    @pytest.fixture(scope="function", autouse=True)
    def player(self, mocker):
        player = pipo.player.Player(None)
        mocker.patch.object(player, "_start_music_queue")
        return player
