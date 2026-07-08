from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models import Area, Course, Stream
from app.routers.requirements import get_db, router as requirements_router
from app.seed import seed_all


def _client_for_db(db):
    app = FastAPI()
    app.include_router(requirements_router)

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_post_progress_on_seeded_data_comp551_comp550_comp558(db):
    seed_all(db)

    # Canonical example courses (stream + 400+ expected).
    ids = (
        db.query(Course.id, Course.code)
        .filter(Course.code.in_(["COMP 551", "COMP 550", "COMP 558"]))
        .all()
    )
    by_code = {code: cid for cid, code in ids}

    payload = {
        "completed_course_ids": [
            by_code["COMP 551"],
            by_code["COMP 550"],
            by_code["COMP 558"],
        ],
        "manual_completed_courses": [],
    }

    client = _client_for_db(db)
    response = client.post("/api/requirements/progress", json=payload)
    assert response.status_code == 200

    data = response.json()

    # All three are 400+ and all are tagged to the Computer Science stream
    # in the seeded dataset.
    assert data["arts_science"]["arts_credits"] == 0
    assert data["arts_science"]["science_credits"] == 11

    assert data["level_400_plus"]["credits"] == 11

    assert data["stream_complementary"]["complementary_credits"] == 0
    assert data["stream_complementary"]["stream_credits"]["Computer Science"] == 11

    # In the current seeded mapping, these three do not contribute to any
    # of the 8 "areas".
    assert data["areas"]["completed_areas"] == []

