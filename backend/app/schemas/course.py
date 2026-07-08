from typing import List, Optional

from pydantic import BaseModel

from app.models.course import Faculty
from app.schemas.stream import StreamResponse
from app.schemas.area import AreaResponse


class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    credits: Optional[int] = None
    level: Optional[int] = None
    faculty: Optional[Faculty] = None
    department: Optional[str] = None


# Used when creating courses
class CourseCreate(CourseBase):
    prerequisite_ids: List[int] = []


# Lightweight representation used for nested references (avoids deep recursion)
class CourseSummary(CourseBase):
    id: int

    class Config:
        from_attributes = True


# Used when returning courses
class CourseResponse(CourseBase):
    id: int
    prerequisites: List[CourseSummary] = []
    streams: List[StreamResponse] = []
    areas: List[AreaResponse] = []

    class Config:
        from_attributes = True
