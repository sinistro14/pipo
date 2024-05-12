from typing import Annotated, List

from pydantic import BaseModel, Field

from pipo.player.audio_source.source_pair import SourcePair

Provider = Annotated[
    str,
    Field(regex=r"^[\d\w]*.[\d\w]*.[\d\w]$")
]

class Prefetch(BaseModel):
    uuid: str = Field(
        regex=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    server_id: str
    shuffle: bool
    source_pairs: List[SourcePair]
