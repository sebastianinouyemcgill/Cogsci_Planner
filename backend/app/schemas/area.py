from pydantic import BaseModel


class AreaBase(BaseModel):
    name: str


class AreaCreate(AreaBase):
    pass


class AreaResponse(AreaBase):
    id: int

    class Config:
        from_attributes = True
