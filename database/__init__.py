from database.base import Base
from database.models import Projects, Directories, Imagery, Changelist, Versions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import join


class ImageryDatabase:
    """
    Functions for manipulating imagery database
    """

    def __init__(self, path):
        self.db_path = join(path, "ivcs.db")
        self.base = Base
        self.engine = None

    def initialize_database(self):
        """
        Set up the database
        :return: None
        """
        self.engine = create_engine("sqlite:///.{}".format(self.db_path))
        Base.metadata.create_all(self.engine)

    def load_session(self):
        """
        Load DB session
        :return: Session object
        """
        self.initialize_database()
        return sessionmaker(bind=self.engine)()
