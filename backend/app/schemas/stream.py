from pydantic import BaseModel


class StreamBase(BaseModel):
    name: str


class StreamCreate(StreamBase):
    pass


class StreamResponse(StreamBase):
    id: int

    class Config:
        from_attributes = True
