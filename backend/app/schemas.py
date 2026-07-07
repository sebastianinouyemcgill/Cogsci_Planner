from pydantic import BaseModel
from typing import List


class CourseBase(BaseModel):
    code: str
    title: str


# Used when returning courses
class CourseResponse(CourseBase):
    id: int
    prerequisites: List["CourseResponse"] = []

    class Config:
        from_attributes = True


# Used when creating courses
class CourseCreate(CourseBase):
    prerequisite_ids: List[int] = []