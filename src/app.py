"""High School Management System API with persistent storage."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine, select

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

DB_PATH = os.getenv("DB_PATH", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DB_PATH.startswith("sqlite") else {}
engine = create_engine(DB_PATH, connect_args=connect_args)

INITIAL_ACTIVITIES: Dict[str, Dict[str, object]] = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


class ActivityParticipant(SQLModel, table=True):
    activity_id: int = Field(foreign_key="activity.id", primary_key=True)
    participant_id: int = Field(foreign_key="participant.id", primary_key=True)


class Activity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    schedule: str
    max_participants: int
    participants: list["Participant"] = Relationship(
        back_populates="activities", link_model=ActivityParticipant
    )


class Participant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    activities: list[Activity] = Relationship(
        back_populates="participants", link_model=ActivityParticipant
    )


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def seed_initial_data() -> None:
    """Load starter activities only if the database is empty."""
    with Session(engine) as session:
        existing_activity = session.exec(select(Activity.id)).first()
        if existing_activity:
            return

        for name, data in INITIAL_ACTIVITIES.items():
            activity = Activity(
                name=name,
                description=data["description"],
                schedule=data["schedule"],
                max_participants=data["max_participants"],
            )
            session.add(activity)
            session.commit()
            session.refresh(activity)

            for email in data["participants"]:
                participant = session.exec(
                    select(Participant).where(Participant.email == email)
                ).first()
                if participant is None:
                    participant = Participant(email=email)
                    session.add(participant)
                    session.commit()
                    session.refresh(participant)

                activity.participants.append(participant)

            session.add(activity)
            session.commit()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    seed_initial_data()


def get_session():
    with Session(engine) as session:
        yield session


def activity_to_dict(activity: Activity) -> Dict[str, object]:
    return {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": [participant.email for participant in activity.participants],
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)):
    activities = session.exec(select(Activity).order_by(Activity.name)).all()
    return {activity.name: activity_to_dict(activity) for activity in activities}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str, email: str, session: Session = Depends(get_session)
):
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    if any(participant.email == email for participant in activity.participants):
        raise HTTPException(status_code=400, detail="Student is already signed up")

    participant = session.exec(select(Participant).where(Participant.email == email)).first()
    if participant is None:
        participant = Participant(email=email)
        session.add(participant)
        session.commit()
        session.refresh(participant)

    activity.participants.append(participant)
    session.add(activity)
    session.commit()
    session.refresh(activity)

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str, email: str, session: Session = Depends(get_session)
):
    activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    participant = session.exec(select(Participant).where(Participant.email == email)).first()
    if participant is None or participant not in activity.participants:
        raise HTTPException(
            status_code=400, detail="Student is not signed up for this activity"
        )

    activity.participants.remove(participant)
    session.add(activity)
    session.commit()
    session.refresh(activity)

    return {"message": f"Unregistered {email} from {activity_name}"}
