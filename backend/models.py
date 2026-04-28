from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
from database import Base
import enum

class TaskStatus(enum.Enum):
    pending = "pending"
    assigned = "assigned"
    done = "done"

class Volunteer(Base):
    __tablename__ = "volunteers"
    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    skills     = Column(String)       # comma-separated: "first_aid,driving"
    latitude   = Column(Float)
    longitude  = Column(Float)
    available  = Column(Boolean, default=True)

class Task(Base):
    __tablename__ = "tasks"
    id             = Column(Integer, primary_key=True)
    title          = Column(String)
    required_skill = Column(String)
    latitude       = Column(Float)
    longitude      = Column(Float)
    urgency        = Column(Integer)  # 1–5, 5 = critical
    lives_at_risk  = Column(Integer)
    status         = Column(Enum(TaskStatus), default=TaskStatus.pending)
    assigned_to    = Column(Integer, nullable=True)  # volunteer ID
    priority_score = Column(Float, default=0.0)
