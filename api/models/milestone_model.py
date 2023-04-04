from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db.base import Base


class Milestones(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, nullable=False)
    description = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)


class StatusDeclaration(Base):
    __tablename__ = "status_declaration"

    id = Column(Integer, primary_key=True, nullable=False)
    milestone_id = Column(Integer, nullable=False)
    unmade = Column(String(255), nullable=False)
    progress = Column(String(255), nullable=False)
    done = Column(String(255), nullable=False)


class Regularizations(Base):
    __tablename__ = "regularization"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer)
    year = Column(Integer)
    status = Column(Integer)
    paid = Column(String(255))
    pending = Column(String(255))
    regimes = Column(String(255))
    periodicity = Column(String(255))
    additional_information = Column(String(255))
