"""
Contains the SQL database definitions
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship


class Imagery(Base):
    