from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Performance
from app.schemas import PerformanceCreate, PerformanceOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="PlayerIQ",
    description=(
        "Football performance intelligence built around measurable evidence, "
        "not vague labels."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "playeriq"}


@app.post(
    "/performances",
    response_model=PerformanceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_performance(
    payload: PerformanceCreate,
    db: Session = Depends(get_db),
):
    performance = Performance(**payload.model_dump())
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance


@app.get("/performances", response_model=list[PerformanceOut])
def list_performances(db: Session = Depends(get_db)):
    statement = select(Performance).order_by(
        Performance.match_date.desc(),
        Performance.id.desc(),
    )
    return list(db.scalars(statement))
