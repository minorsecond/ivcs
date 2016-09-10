from database.base import Base
from database.models import Projects, Directories, Imagery, Changelist, Versions, Checkouts, \
    Tasklists, projects_associations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import join


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
    Methods for querying the database
    """

    def __init__(self, path):
        self.db_filter = None
        db_init = ImageryDatabase(path)

        self.session = db_init.load_session()

    def query_projects(self):
        """
        Queries the projects table
        :return: List of projects
        """
        print(self.session.query(Projects).order_by(Projects.name).all())
        return self.session.query(Projects)
