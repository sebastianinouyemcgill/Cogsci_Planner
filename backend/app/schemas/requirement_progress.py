from typing import Dict, List, Literal

from pydantic import BaseModel, Field


FacultyName = Literal["Arts", "Science"]


class ManualCompletedCourseInput(BaseModel):
    """
    A manually-entered non-major (or otherwise external) completed course.

    This supports Arts/Science totals from all completed coursework, not only
    the seeded Cognitive Science course table.
    """

    code: str
    credits: int = Field(ge=0)
    faculty: FacultyName
    level: int = Field(default=0, ge=0)


class RequirementsProgressRequest(BaseModel):
    """
    Input contract for progress evaluation.

    - `completed_course_ids`: IDs of completed courses from the DB.
    - `manual_completed_courses`: extra completed courses that are not in the DB.
    """

    completed_course_ids: List[int] = []
    manual_completed_courses: List[ManualCompletedCourseInput] = []


class ArtsScienceProgress(BaseModel):
    arts_credits: int
    science_credits: int


class LevelProgress(BaseModel):
    threshold: int
    credits: int
    course_ids: List[int]


class StreamComplementaryProgress(BaseModel):
    stream_credits: Dict[str, int]
    complementary_credits: int
    course_bucket: Dict[int, str]


class AreasProgress(BaseModel):
    required_areas: List[str]
    completed_areas: List[str]


class RequirementsProgressResponse(BaseModel):
    arts_science: ArtsScienceProgress
    level_400_plus: LevelProgress
    stream_complementary: StreamComplementaryProgress
    areas: AreasProgress

