"""
Contains the SQL database definitions
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy.orm import relationship
from database.base import Base


class Users(Base):
    """
    Stores usernames
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    checkouts = relationship("checkouts", back_populates="checkouts")


class Projects(Base):
    """
    Table for storing all projects (will be stored on users local machine)
    """

    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    working_directory = Column(String)


class Directories(Base):
    """
    Stores the directory structures associated with projects
    """

    __tablename__ = "directories"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    root = Column(String)


class Imagery(Base):
    """
    Stores the image file data
    """

    __tablename__ = "imagery"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    image_path = Column(String)
    image_extension = Column(String)
    image_size = Column(Float)
    image_hash = Column(String)
    image_modified_time = Column(DateTime)
    image_first_seen = Column(DateTime)
    image_last_scanned = Column(DateTime)
    image_on_disk = Column(Boolean)


class Changelist(Base):
    """
    Stores all changes made to file
    """

    __tablename__ = "changelist"
    id = Column(Integer)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    image_id = Column(Integer, ForeignKey("imagery.id"))
    change_type = Column(Integer)  # 0->added 1-> modified 2-> deleted
    change_time = Column(DateTime)


class Versions(Base):
    """
    Stores the image file version data
    """

    __tablename__ = "versions"
    id = Column(Integer)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    directory_id = Column(Integer, ForeignKey("directories.id"))
    image_id = Column(Integer, ForeignKey("imagery.id"))
    change_id = Column(String, ForeignKey("changelist.id"))
    checkout_id = Column(Integer, ForeignKey("checkouts.id"))
    path_to_version = Column(String)
    commit_message = Column(String)


class Checkouts(Base):
    """
    Stores checkout status
    """

    __tablename__ = "checkouts"
    id = Column(Integer)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    image_id = Column(Integer, ForeignKey("imagery.id"))
    checked_out_by = relationship("users", back_populates="checkouts")
    checked_out_date = Column(DateTime)
    checked_in_date = Column(DateTime)


class Tasklists(Base):
    """
    Stores tasks that are repeated (for drop-down menu)
    """

    __tablename__ = "tasklits"
    id = Column(Integer, primary_key=True)
    taskname = Column(String)
    task_description = Column(String)
