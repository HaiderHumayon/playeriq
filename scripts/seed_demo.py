from datetime import date

from sqlalchemy import delete, select

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import AIAnalysis, LLMUsageLog, Performance, User

DEMO_EMAIL = "demo@playeriq.local"
DEMO_PASSWORD = "PlayerIQDemo9!"
DEMO_PLAYER = "Demo Midfielder"


def run() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(User.email == DEMO_EMAIL)
        )

        if user is None:
            user = User(
                email=DEMO_EMAIL,
                player_name=DEMO_PLAYER,
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.flush()
        else:
            user.player_name = DEMO_PLAYER
            user.password_hash = hash_password(DEMO_PASSWORD)
            db.flush()

        db.execute(
            delete(AIAnalysis).where(
                AIAnalysis.user_id == user.id
            )
        )
        db.execute(
            delete(LLMUsageLog).where(
                LLMUsageLog.user_id == user.id
            )
        )
        db.execute(
            delete(Performance).where(
                Performance.user_id == user.id
            )
        )

        old_ratings = [6.6, 6.7, 6.8, 6.9, 7.0]
        new_ratings = [7.4, 7.6, 7.8, 8.0, 8.2]

        for index, rating in enumerate(
            old_ratings,
            start=1,
        ):
            db.add(
                Performance(
                    user_id=user.id,
                    player_name=DEMO_PLAYER,
                    match_date=date(2026, 7, index),
                    opponent=f"Previous Opponent {index}",
                    position="CM",
                    minutes_played=90,
                    goals=0,
                    assists=0,
                    shots=1,
                    key_passes=1,
                    tackles=2,
                    interceptions=1,
                    rating=rating,
                    rpe=7,
                    notes="Synthetic previous-form demo record.",
                )
            )

        for index, rating in enumerate(
            new_ratings,
            start=1,
        ):
            db.add(
                Performance(
                    user_id=user.id,
                    player_name=DEMO_PLAYER,
                    match_date=date(2026, 8, index),
                    opponent=f"Current Opponent {index}",
                    position="CM",
                    minutes_played=90,
                    goals=1 if index in (3, 5) else 0,
                    assists=1 if index in (2, 4) else 0,
                    shots=3,
                    key_passes=3,
                    tackles=4,
                    interceptions=2,
                    rating=rating,
                    rpe=8,
                    notes="Synthetic current-form demo record.",
                )
            )

        db.commit()

    print("PLAYERIQ DEMO DATA READY")
    print(f"Email: {DEMO_EMAIL}")
    print(f"Password: {DEMO_PASSWORD}")
    print("Synthetic records: 10")


if __name__ == "__main__":
    run()
