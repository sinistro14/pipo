from typing import Any, Dict, List, Optional

from pydantic import AfterValidator, BaseModel
from typing_extensions import Annotated


class SpotifyArtist(BaseModel):
    name: str


class SpotifyTrack(BaseModel):
    name: str
    artists: Optional[List[SpotifyArtist]]


def get_track(v: Any) -> SpotifyTrack:
    return v.get("track", None)


CustomTrack = Annotated[
    Dict[str, SpotifyTrack],
    AfterValidator(get_track),
]


class SpotifyPlaylist(BaseModel):
    items: List[CustomTrack]


class SpotifyAlbum(BaseModel):
    items: List[SpotifyTrack]
