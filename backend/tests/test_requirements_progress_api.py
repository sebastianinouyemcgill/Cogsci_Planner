from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models import Course, Faculty
from app.routers.requirements import get_db, router as requirements_router


def _client_for_db(db):
    app = FastAPI()
    app.include_router(requirements_router)

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_get_progress_contract_shape_returns_baseline(db):
    client = _client_for_db(db)

    response = client.get("/api/requirements/progress")
    assert response.status_code == 200

    payload = response.json()
    assert set(payload.keys()) == {
        "arts_science",
        "level_400_plus",
        "stream_complementary",
        "areas",
    }
    assert payload["arts_science"]["arts_credits"] == 0
    assert payload["arts_science"]["science_credits"] == 0
    assert payload["level_400_plus"]["threshold"] == 400


def test_post_progress_uses_db_courses_and_manual_courses(db):
    # DB course contributes to stream and science credits.
    db_course = Course(
        code="COMP 551",
        title="Applied Machine Learning",
        credits=4,
        level=551,
        faculty=Faculty.SCIENCE,
        department="Computer Science",
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    client = _client_for_db(db)
    response = client.post(
        "/api/requirements/progress",
        json={
            "completed_course_ids": [db_course.id],
            "manual_completed_courses": [
                {
                    "code": "PHIL 210",
                    "credits": 3,
                    "faculty": "Arts",
                    "level": 210,
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()

    # Arts/science should include BOTH DB and manual completed courses.
    assert payload["arts_science"]["arts_credits"] == 3
    assert payload["arts_science"]["science_credits"] == 4

    # 400+ should include COMP551 only.
    assert payload["level_400_plus"]["credits"] == 4

