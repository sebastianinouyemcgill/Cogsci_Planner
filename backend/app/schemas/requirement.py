from pydantic import BaseModel


class RequirementBase(BaseModel):
    name: str
    type: str
    credits_required: int


class RequirementCreate(RequirementBase):
    pass


class RequirementResponse(RequirementBase):
    id: int

    class Config:
        from_attributes = True
