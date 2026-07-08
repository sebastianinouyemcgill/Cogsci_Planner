"""initial academic data model

Creates the full Phase 1 schema: courses (with level/faculty/department/
credits), streams, areas, requirements, and the join tables for
prerequisites, course-streams, and area-courses.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


faculty_enum = sa.Enum("Arts", "Science", name="faculty")


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credits", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("faculty", faculty_enum, nullable=True),
        sa.Column("department", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_courses_id", "courses", ["id"])
    op.create_index("ix_courses_code", "courses", ["code"], unique=True)

    op.create_table(
        "streams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_streams_id", "streams", ["id"])
    op.create_index("ix_streams_name", "streams", ["name"], unique=True)

    op.create_table(
        "areas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_areas_id", "areas", ["id"])
    op.create_index("ix_areas_name", "areas", ["name"], unique=True)

    op.create_table(
        "requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("credits_required", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_requirements_id", "requirements", ["id"])
    op.create_index("ix_requirements_name", "requirements", ["name"], unique=True)

    op.create_table(
        "course_prerequisites",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("prerequisite_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["prerequisite_id"], ["courses.id"]),
        sa.PrimaryKeyConstraint("course_id", "prerequisite_id"),
    )

    op.create_table(
        "course_streams",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("stream_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"]),
        sa.PrimaryKeyConstraint("course_id", "stream_id"),
    )

    op.create_table(
        "area_courses",
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["areas.id"]),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.PrimaryKeyConstraint("area_id", "course_id"),
    )


def downgrade() -> None:
    op.drop_table("area_courses")
    op.drop_table("course_streams")
    op.drop_table("course_prerequisites")

    op.drop_index("ix_requirements_name", table_name="requirements")
    op.drop_index("ix_requirements_id", table_name="requirements")
    op.drop_table("requirements")

    op.drop_index("ix_areas_name", table_name="areas")
    op.drop_index("ix_areas_id", table_name="areas")
    op.drop_table("areas")

    op.drop_index("ix_streams_name", table_name="streams")
    op.drop_index("ix_streams_id", table_name="streams")
    op.drop_table("streams")

    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_index("ix_courses_id", table_name="courses")
    op.drop_table("courses")

    faculty_enum.drop(op.get_bind(), checkfirst=True)
