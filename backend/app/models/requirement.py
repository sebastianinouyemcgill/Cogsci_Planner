from sqlalchemy import Column, Integer, String

from app.database import Base


class Requirement(Base):
    """A degree-level rule (not a simple course list).

    Examples: Stream Requirement (18 credits), 400-Level Requirement
    (15 credits where level >= 400), Arts Requirement (21 Arts credits).
    Evaluation logic against these rules lives in services/, not here.
    """

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Rule category, e.g. "stream", "level_threshold", "faculty".
    type = Column(String)
    credits_required = Column(Integer)
