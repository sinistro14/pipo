from pydantic import BaseModel, Field, HttpUrl


class Music(BaseModel):
    uuid: str = Field(
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    provider: str = Field(pattern=r"^[\d\w]*.[\d\w]*.[\d\w]*$")
    server_id: str
    operation: str
    source: HttpUrl