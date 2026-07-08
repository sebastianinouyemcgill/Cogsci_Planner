"""Run the seed script:  python -m app.seed"""

from app.database import SessionLocal
from app.seed.seeder import seed_all


def main() -> None:
    db = SessionLocal()
    try:
        summary = seed_all(db)
    finally:
        db.close()

    print(
        "Seed complete: "
        f"{summary['streams']} streams, "
        f"{summary['areas']} areas, "
        f"{summary['courses']} courses, "
        f"{summary['requirements']} requirements."
    )
    for warning in summary["warnings"]:
        print(f"  warning: {warning}")


if __name__ == "__main__":
    main()
