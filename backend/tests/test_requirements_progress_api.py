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


def _progress_keys():
    return {
        "arts_science",
        "level_400_plus",
        "stream_complementary",
        "official_stream_complementary",
        "electives",
        "areas",
    }


def test_get_progress_contract_shape_returns_baseline(db):
    client = _client_for_db(db)

    response = client.get("/api/requirements/progress")
    assert response.status_code == 200

    payload = response.json()
    assert set(payload.keys()) == {"completed", "projected"}

    for view in ("completed", "projected"):
        assert set(payload[view].keys()) == _progress_keys()
        assert payload[view]["arts_science"]["arts_credits"] == 0
        assert payload[view]["arts_science"]["science_credits"] == 0
        assert payload[view]["level_400_plus"]["threshold"] == 400


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
            "courses": [{"course_id": db_course.id, "status": "completed"}],
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

    for view in ("completed", "projected"):
        # Arts/science should include BOTH DB and manual completed courses.
        assert payload[view]["arts_science"]["arts_credits"] == 3
        assert payload[view]["arts_science"]["science_credits"] == 4

        # 400+ should include COMP551 only.
        assert payload[view]["level_400_plus"]["credits"] == 4
