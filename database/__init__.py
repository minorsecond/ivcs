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
                            raise ValueError("Returned user id that does not match what was "
                                             "requested in query_objects_for_user()")

        return set(project_ids)

    def get_all_projects(self):
        """
        Returns a list of all project names and IDs
        :return: list
        """

        projects_info = []

        projects = self.session.query(Projects).all()

        for project in projects:
            project_id = project.id
            project_name = project.name

            project_info = (project_id, project_name)
            projects_info.append(project_info)

        return projects_info

    def get_users_for_project(self, project):
        """
        Gets the users associated with a specific project
        :return: List of usernames associated with a project ID (project.id, project.name, username)
        """

        users_per_project = []
        associations = None

        project = self.session.query(Projects).filter_by(name=project).first()

        try:
            associations = self.session.query(user_projects).filter_by(project_id=project.id)

        except Exception as e:  # TODO: Make this specific to sqlalchemy.exc.InvalidRequestError
            logging.warning("Error querying the project_users table in get_users_for_project. "
                            "Perhaps there are no users assigned to project.")
            print(e)

        for association in associations:
            project_id = association.project_id
            project_name = project.name
            user_id = association.user_id
            user = self.session.query(Users).filter_by(id=user_id).one()

            try:
                user_name = user.username
                result = (project_id, project_name, user_name)
                users_per_project.append(result)

            except AttributeError as e:
                text = "Could not find row in Users db for user {0} when trying to get users " \
                       "for project {1}. Perhaps the project is not associated with any users. " \
                       "The function returned: {2}".format(user_id, project_name, e)

                logging.info(text)
                print(text)

        return users_per_project

    def get_directories_for_project(self, project):
        """
        Gets the directories associated with a project
        :param project: project id
        :return: List of directories associated with project
        """

        directories_in_project = []
        directories = None

        project = self.session.query(Projects).filter_by(id=project).first()

        try:
            directories = self.session.query(Directories).filter_by(project_id=project.id).all()
        except Exception as e:  # TODO: Make this specific to sqlalchemy error
            logging.warning("Error querying the project_users table in get_users_for_project. "
                            "Perhaps there are no users assigned to project.")
            print(e)

        for entry in directories:
            directory = entry.root
            project_id = entry.project_id
            result = (project_id, directory)

            directories_in_project.append(result)

        return directories_in_project
