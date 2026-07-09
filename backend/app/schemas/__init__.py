from app.schemas.course import (
    CourseBase,
    CourseCreate,
    CourseSummary,
    CourseResponse,
)
from app.schemas.stream import StreamBase, StreamCreate, StreamResponse
from app.schemas.area import AreaBase, AreaCreate, AreaResponse
from app.schemas.requirement import (
    RequirementBase,
    RequirementCreate,
    RequirementResponse,
)
from app.schemas.requirement_progress import (
    ManualCompletedCourseInput,
    CourseProgressEntry,
    RequirementsProgressRequest,
    ArtsScienceProgress,
    CourseBucketAllocation,
    ElectivesProgress,
    HonoursResearchProgress,
    LevelProgress,
    StreamComplementaryProgress,
    AreasProgress,
    OfficialStreamComplementaryProgress,
    RequirementProgressBreakdown,
    RequirementsProgressResponse,
)

__all__ = [
    "CourseBase",
    "CourseCreate",
    "CourseSummary",
    "CourseResponse",
    "StreamBase",
    "StreamCreate",
    "StreamResponse",
    "AreaBase",
    "AreaCreate",
    "AreaResponse",
    "RequirementBase",
    "RequirementCreate",
    "RequirementResponse",
    "ManualCompletedCourseInput",
    "CourseProgressEntry",
    "RequirementsProgressRequest",
    "ArtsScienceProgress",
    "CourseBucketAllocation",
    "ElectivesProgress",
    "HonoursResearchProgress",
    "LevelProgress",
    "StreamComplementaryProgress",
    "AreasProgress",
    "OfficialStreamComplementaryProgress",
    "RequirementProgressBreakdown",
    "RequirementsProgressResponse",
]
