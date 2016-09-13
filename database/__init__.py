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

    def query_all_users(self):
        """
        Returns a list of all users in DB
        :return: List
        """

        try:
            all_users = self.session.query(Users).all()
            return all_users
        except Exception as e:
            text = "Failed returning all users in database/__init__.py/query_all_users(). The " \
                   "function returned: {}".format(e)
            print(text)
            logging.error(text)

    def query_users(self, user):
        """
        Queries the projects table
        :param user: Username to query
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

    def get_project_id_by_name(self, project_name):
        """
        Gets the project id from the project name
        :return: int
        """

        project = self.session.query(Projects).filter_by(name=project_name).first()

        return project.id

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

        if directories:
            for entry in directories:
                directory = entry.root
                project_id = entry.project_id
                result = (project_id, directory)

                directories_in_project.append(result)

        return directories_in_project

    def add_new_project(self, project_name):
        """
        Add a new project to database
        :param name: Name of new project
        :return: None
        """
        current_project_names = []
        current_projects = self.get_all_projects()

        for project in current_projects:
            current_project_names.append(project[1])

        if project_name not in current_project_names:
            new_project = Projects(
                name=project_name
            )

            self.session.add(new_project)
            self.session.commit()
            return 0
        else:
            return 1

    def delete_project(self, project):
        """
        Deletes project from database
        :param project: a project name
        :return: None
        """

        self.session.query(Projects).filter_by(name=project).delete()
        self.session.commit()

    def add_project_directory(self, project, path):
        """
        Adds a directory to the project
        :return: id of new row
        """

        current_directories = []
        project_id = self.get_project_id_by_name(project)
        cdir = self.get_directories_for_project(project_id)

        for item in cdir:
            current_directories.append(item[1])

        if path not in current_directories:

            new_directory = Directories(
                project_id=project_id,
                root=path
            )

            self.session.add(new_directory)
            self.session.commit()

            return new_directory.id

        else:
            text = "User attempted to enter a directory that was already specified for project: " \
                   "{}".format(path)
            logging.warning(text)
            print(text)

            return None

    def delete_project_directory(self, project_name, selected_dir):
        """
        Deletes a directory reference for a project
        :return: None
        """

        proj_id = self.get_project_id_by_name(project_name)
        self.session.query(Directories).filter_by(project_id=proj_id, root=selected_dir).delete()
        self.session.commit()

    def add_new_user(self, user_info):
        """
        Add a new user to the database
        :param user_info: a dict containing {name: {FULLNAME}, username: {USERNAME},
        password: {PASSWORD}, email: {EMAIL ADDRESS}}
        :return: code: -1 -> username already exists. -2 -> email already exists. 0 -> success
        """
        result = None
        name = user_info['name']
        uname = user_info['username']
        pword = user_info['password']
        email_address = user_info['email']

        # Check if any of the values are already in the db
        current_users = self.query_users(uname)
        try:
            current_email = result = self.session.query(Users).filter_by(email=email_address).one()

            if uname == current_users:
                result = -1

            elif email_address == current_email.email:
                result = -2

        except exc.NoResultFound:
            pass  # This is good! We don't want there to be another instance of this.

        if result is None:
            try:
                new_user = Users(
                    full_name=name,
                    username=uname,
                    password=pword,
                    email=email_address
                )

                print(name)
                print(uname)
                print(pword)
                print(email_address)

                self.session.add(new_user)
                self.session.commit()

                result = 0

            except Exception as e:
                text = "Could not add new user to database. The add_new_user function returned " \
                       "{}".format(e)
                logging.warning(text)
                print(text)

        return result

    def validate_password_input(self, uname, password):
        """
        Validates user's password input against stored hash
        :return:
        """
        user_table = Users()
        user = self.session.query(Users).filter_by(username=uname).one()
        return user.verify_password(password)

    def query_all_tasks(self):
        """
        Returns list of tuples containing projects and tasks
        :return: [(project_name, task_name) .. ]
        """

        task_list = []
        tasks = self.session.query(Tasklists).all()

        for task in tasks:
            project_name = task.project
            task_id = task.id
            task_name = task.taskname

            project = self.session.query(Projects).filter_by(name=project_name).one()
            project_name = project.name

            result = (project_name, task_name)
            task_list.append(result)

        return task_list

    def get_task_by_project(self, project_id):
        """Get list of tasks by project"""
        taskllist = []
        tasks = self.session.query(Tasklists).filter_by(project_id=project_id).all()
        for task in tasks:
            task_name = task.taskname
            print(task_name)
            taskllist.append(task_name)

        return taskllist

    def get_task_id(self, task_name):
        """
        Gets the ID number of the task name
        :param task_name: string denoting task name
        :return: Int
        """

        task = self.session.query(Tasklists).filter_by(taskname=task_name).one()
        return task

    def add_new_task(self, task_info):
        """
        Adds a new task to the DB
        :return: None

        The task_info dict is in the form:
        new_task = {
                'task_name':            task_name,
                'project':              project,
                'blocks':               blocks,
                'blocked_by':           blocked_by,
                'input_directory':      input_directory,
                'output_directory':     output_directory,
                'estimated_completion': estimated_completion
            }
        """

        task_name = task_info['task_name']
        #task_description = task_info['task_description']  #TODO: Enable this
        task_input_directory = task_info['input_directory']
        task_output_directory = task_info['output_directory']  #TODO: Enable this
        project = task_info['project']
        #estimated_completion = task_info['estimated_completion']

        new_task = Tasklists(
            taskname=task_name,
            #task_description=None,  # TODO: Enable this
            #task_output_directory=task_output_directory,
            project=project,
            task_input_directory=task_input_directory,
            task_output_directory=task_output_directory
            #estimated_completion=estimated_completion
        )

        self.session.add(new_task)
        self.session.commit()

    def delete_task(self, task_name):
        """
        Delete a task from the database
        :param task_name: Task.name
        :return: None
        """
        task_id = (self.get_task_id(task_name)).id
        self.session.query(Tasklists).filter_by(id=task_id).delete()
        self.session.commit()

        # TODO: Add code to blocker/blockee

    def add_file_to_database(self, file_info):
        """
        Adds file to database
        :param file_info: dict with structure:

        'project_id':               project_id,
                'directory_id':             new_directory_id,
                'image_path':               image_path,
                'image_extension':          image_extension,
                'image_size':               image_size,
                'image_hash':               image_hash,
                'image_modification_time':  image_modification_time,
                'image_first_seen':         image_first_seen,
                'image_last_scanned':       image_last_scanned,
                'image_on_disk':            image_on_disk

        :return:
        """
        # First, check that file isn't already in DB.
        new_file = Imagery(
            project_id=file_info['project_id'],
            directory_id=file_info['directory_id'],
            image_path = file_info['image_path'],
            image_extension = file_info['image_extension'],
            image_size = file_info['image_size'],
            image_hash = file_info['image_hash'],
            image_modified_time = file_info['image_modification_time'],
            image_first_seen = file_info['image_first_seen'],
            image_last_scanned = file_info['image_last_scanned'],
            image_on_disk = file_info['image_on_disk']
        )

        self.session.add(new_file)
        self.session.commit()

    def get_all_remote_files(self):
        """Get a list of all remote files"""
        files = []
        file_query = self.session.query(Imagery).all()

        for file in file_query:
            file_path = file.image_path
            file_project = file.project_id

            files.append((file_path, file_project))

        return files

    def check_file_hash(self, file, current_hash):
        """Checks the file hash in the db against current hash"""
        file = self.session.query(Imagery).filter_by(image_path=file).one()

        return file.image_hash == current_hash
