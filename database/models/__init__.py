"""
Contains the SQL database definitions
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from database.base import Base


class Projects(Base):
    """
    Table for storing all projects (will be stored on users local machine)
    """

    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)

