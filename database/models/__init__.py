"""
Contains the SQL database definitions
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, ForeignKeyConstraint
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from database.base import Base
from database.passwords import Password
import bcrypt

__all__ = ['projects_associations', 'Users', 'Projects', 'Directories', 'Imagery', 'Changelist',
           'Versions', 'Checkouts', 'Tasklists']

# This stores associations between tasks and projects (many to many)
project_tasks = Table("tasks-projects_associations", Base.metadata,
                      Column("project_id", Integer, ForeignKey("Projects.id")),
                      Column("task_id", Integer, ForeignKey("TaskLists.id")))

user_projects = Table("user-projects_associations", Base.metadata,
                      Column("user_id", Integer, ForeignKey("Users.id")),
                      Column("project_id", Integer, ForeignKey("Projects.id")))


class Users(Base):
    """
    Stores usernames
    """

    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    username = Column(String)
    password = Column(Password)
    email = Column(String)
    role = Column(Integer)
    checkouts = relationship("Checkouts")
    projects = relationship("Projects", secondary=user_projects)

    @validates('password')
    def _validate_password(self, key, password):
        return getattr(type(self), key).type.validator(password)


class Projects(Base):
    """
    Table for storing all projects (will be stored on users local machine)
    """

    __tablename__ = "Projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    working_directory = Column(String)
    tasks = relationship("Tasklists", secondary=project_tasks)


class Directories(Base):
    """
    Stores the directory structures associated with projects. Each will be linked to a project, and
    will be scanned for file changes.
    """

    __tablename__ = "Directories"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Projects.id"))
    root = Column(String)


class Imagery(Base):
    """
    Stores the image file data
    """

    __tablename__ = "Imagery"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Projects.id"))
    directory_id = Column(Integer, ForeignKey("Directories.id"))
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

    __tablename__ = "Changelist"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Projects.id"))
    directory_id = Column(Integer, ForeignKey("Directories.id"))
    image_id = Column(Integer, ForeignKey("Imagery.id"))
    change_type = Column(Integer)  # 0->added 1-> modified 2-> deleted
    change_time = Column(DateTime)


class Versions(Base):
    """
    Stores the image file version data
    """

    __tablename__ = "Versions"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Projects.id"))
    directory_id = Column(Integer, ForeignKey("Directories.id"))
    image_id = Column(Integer, ForeignKey("Imagery.id"))
    change_id = Column(String, ForeignKey("Changelist.id"))
    checkout_id = Column(Integer, ForeignKey("Checkouts.id"))
    path_to_version = Column(String)
    commit_message = Column(String)


class Checkouts(Base):
    """
    Stores checkout status
    """

    __tablename__ = "Checkouts"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("Projects.id"))
    image_id = Column(Integer, ForeignKey("Imagery.id"))
    user_id = Column(Integer, ForeignKey("Users.id"))
    checked_out_date = Column(DateTime)
    checked_in_date = Column(DateTime)


class Tasklists(Base):
    """
    Stores tasks that are repeated (for drop-down menu)
    """

    __tablename__ = "TaskLists"
    id = Column(Integer, primary_key=True)
    taskname = Column(String)
    task_description = Column(String)
    task_output_directory = Column(String)
    projects = relationship("Projects", secondary=project_tasks)
    task_complete = Column(Boolean)


class TaskDependencies(Base):
    """
    Relationships between tasks that denote dependencies
    """

    __tablename__ = "TaskDependencies"
    id = Column(Integer, primary_key=True)
    task = Column(Integer, ForeignKey("TaskLists.id"))
    dependency = Column(Integer, ForeignKey("TaskLists.id"))
