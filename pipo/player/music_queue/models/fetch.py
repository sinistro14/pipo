from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl

Operation = Annotated[
    str,
    Field(regex=r"^[\d\w]*.[\d\w]*.[\d\w]$")
]

class Fetch(BaseModel):
    uuid: str = Field(
        regex=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    server_id: str
    provider: str   # TODO enum later
    operation: str  # TODO enum later
    query: HttpUrl
