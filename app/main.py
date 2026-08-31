from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.analytics import build_summary
from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import Base, engine, get_db
from app.models import Performance, User
from app.schemas import (
    AnalyticsSummary,
    PerformanceCreate,
    PerformanceOut,
    RegisterRequest,
    TokenOut,
    UserOut,
)


def apply_m3_schema() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE performances "
                "ADD COLUMN IF NOT EXISTS user_id INTEGER"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_performances_user_id ON performances (user_id)"
            )
        )
        connection.execute(
            text("DELETE FROM performances WHERE user_id IS NULL")
        )
        connection.execute(
            text(
                "ALTER TABLE performances "
                "ALTER COLUMN user_id SET NOT NULL"
            )
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    apply_m3_schema()
    yield


app = FastAPI(
    title="PlayerIQ",
    description=(
        "Football performance intelligence built around measurable evidence, "
        "not vague labels."
    ),
    version="0.3.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "playeriq"}


@app.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = User(
        email=str(payload.email).lower(),
        player_name=payload.player_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form.username.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenOut(access_token=create_access_token(user))


@app.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post(
    "/performances",
    response_model=PerformanceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_performance(
    payload: PerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    performance = Performance(
        **payload.model_dump(),
        user_id=current_user.id,
        player_name=current_user.player_name,
    )
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance


@app.get("/performances", response_model=list[PerformanceOut])
def list_performances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Performance)
        .where(Performance.user_id == current_user.id)
        .order_by(
            Performance.match_date.desc(),
            Performance.id.desc(),
        )
    )
    return list(db.scalars(statement))


@app.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(
    window: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = list(
        db.scalars(
            select(Performance)
            .where(Performance.user_id == current_user.id)
            .order_by(
                Performance.match_date.desc(),
                Performance.id.desc(),
            )
            .limit(window * 2)
        )
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No performance data available for analysis",
        )

    return build_summary(rows, window)
