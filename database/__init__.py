from database.base import Base
from database.models import Projects, Directories, Imagery, Changelist, Versions, Checkouts, \
    Tasklists
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
