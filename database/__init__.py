from database.base import Base
from database.models import Users, Projects, Directories, Imagery, Changelist, Versions, \
    Checkouts, Tasklists, project_tasks, user_projects
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc
from os.path import join
import logging

class ImageryDatabase:
    """
    Functions for manipulating imagery database
    """

    def __init__(self, path):
        self.base = Base
        self.db_path = join(path, "ivcs.db")
        self.engine = create_engine("sqlite:///{}".format(self.db_path))
        base.Base.metadata.create_all(self.engine, checkfirst=True)
        self._session = sessionmaker(bind=self.engine)
        self.session = self._session()

    def load_session(self):
        """
        Load DB session
        :return: Session object
        """

        return self.session


class DatabaseQueries:
    """
    Methods for querying the database. These will mostly be used on program init - to populate
    the tool with data.
    """

    def __init__(self, path):
        self.db_filter = None
        db_init = ImageryDatabase(path)
        self.session = db_init.load_session()

    def query_users(self, user):
        """
        Queries the projects table
        :return: List of projects
        """

        result = None

        try:
            result = self.session.query(Users).filter_by(username=user).one()

        except exc.NoResultFound:
            print("Could not find any results for user '{}' in query_users().".
                                    format(user))
            result = ValueError

        return result

    def query_projects_for_user(self, username):
        """
        Queries the projects table
        :return: List of project ids that user is involved in
        """

        project_ids = []

        if username:  # Get projects for user
            user = self.query_users(username)

            if user:
                if user == ValueError:
                    return user
                else:
                    uid = user.id

                    projects_for_user = self.session.query(user_projects).filter_by(user_id=uid).all()

                    for item in projects_for_user:
                        user_id = item[0]
                        project_id = item[1]

                        if user_id == uid:
                            project_ids.append(project_id)

                        else:
                            raise ValueError("Returned user id that does not match what was requested in "
                                             "query_objects_for_user()")

        return set(project_ids)
