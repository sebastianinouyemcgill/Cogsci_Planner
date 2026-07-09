from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


FacultyName = Literal["Arts", "Science"]
CourseStatus = Literal["planned", "completed"]


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


class CourseProgressEntry(BaseModel):
    """A DB course with its completion status."""

    course_id: int
    status: CourseStatus
    bucket_override: Optional[str] = None


class RequirementsProgressRequest(BaseModel):
    """
    Input contract for progress evaluation.

    - `courses`: DB courses with status `completed` or `planned`.
    - `manual_completed_courses`: extra completed courses that are not in the DB.
    - `declared_stream`: when set, official Stream/Complementary allocation uses
      only this stream; when null, a provisional stream is auto-selected.
    """

    courses: List[CourseProgressEntry] = []
    manual_completed_courses: List[ManualCompletedCourseInput] = []
    honours_enabled: bool = False
    declared_stream: Optional[str] = None


class ArtsScienceProgress(BaseModel):
    arts_credits: int
    science_credits: int


class LevelProgress(BaseModel):
    threshold: int
    credits: int
    course_ids: List[int]


class CourseBucketAllocation(BaseModel):
    eligible_buckets: List[str]
    allocated_bucket: Optional[str] = None


class StreamComplementaryProgress(BaseModel):
    stream_credits: Dict[str, int]
    complementary_credits: int
    course_bucket: Dict[int, str]
    course_allocations: Dict[int, CourseBucketAllocation]


class OfficialStreamComplementaryProgress(BaseModel):
    """Official declared/provisional stream + complementary allocation."""

    declared_stream: Optional[str] = None
    stream_is_provisional: bool
    provisional_stream: Optional[str] = None
    stream_credits: int
    stream_credit_required: int = 18
    complementary_credits: int
    complementary_credit_required: int = 12
    course_bucket: Dict[int, str]
    course_allocations: Dict[int, CourseBucketAllocation]


class ElectivesProgress(BaseModel):
    credits: int
    course_ids: List[int]


class AreasProgress(BaseModel):
    required_areas: List[str]
    completed_areas: List[str]
    area_course_ids: Dict[str, int]


class HonoursResearchProgress(BaseModel):
    required_credits: int
    credits: int
    remaining_credits: int
    course_ids: List[int]
    satisfied: bool


class RequirementProgressBreakdown(BaseModel):
    """Progress computed from a single course set (completed-only or projected)."""

    arts_science: ArtsScienceProgress
    level_400_plus: LevelProgress
    stream_complementary: StreamComplementaryProgress
    official_stream_complementary: OfficialStreamComplementaryProgress
    electives: ElectivesProgress
    areas: AreasProgress
    honours_research: Optional[HonoursResearchProgress] = None


class RequirementsProgressResponse(BaseModel):
    completed: RequirementProgressBreakdown
    projected: RequirementProgressBreakdown

