import os
import json
import fire
from datetime import datetime
DB_FILE = 'db.json'
ENV_FILE = 'env.json'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Database(object):
    """Storage class to keep track of gist sync information.

    This class is independent of the actual implementation
    of the database, thus make it easier to change in the future.
    """

    def __init__(self):
        if not os.path.isfile(DB_FILE):
            self.info = {"num_gists": 0}
            self.env = {
                "cold_start": True,
                "sync_at": datetime.strftime(datetime(1990, 10, 22), DATE_FORMAT)}
            self.sync_env("save")
            return

        # restore db and env from previous execution result
        self.sync_info('load')
        self.sync_env('load')

    def is_empty(self):
        """Indicate whether there is any gist in database.

        Returns
        -------
        bool

        """
        return self.info.get('num_gists', 0) == 0

    def is_cold_start(self):
        """Indicate whether it is needed to synchronize all gists.

        Returns
        -------
        bool

        """
        return self.env.get('cold_start', True)

    def sync_at(self):
        """Return the UTC datetime indicating the last synchronization

        Returns
        -------
        last_sync_date : datetime.datetime
        """
        return datetime.strptime(self.env['sync_at'], DATE_FORMAT)

    def toggle_cold_start(self):
        """Toggle value of cold_start"""
        self.env['cold_start'] = not self.env.get('cold_start', True)
        self.sync_env('save')

    def get_hash_by_id(self, gist_id):
        """Get hash value of the gist using `gist_id` as key

        Parameters
        ----------
        gist_id : str
            Unique gist identifier called `id` available in Github API
            e.g. "MDQ6R2lzdGUzOTNkODgxMjIyODg1ZjU5ZWYwOWExNDExNzE1OWM4"

        Returns
        -------
        hash : str
            "" if no gist can be found in database by `gist_id`
        """
        return self.info.get(gist_id, {}).get('hash', '')

    def get_note_guid_by_id(self, gist_id):
        """Get guid of note related to the gist with `gist_id`

        Parameters
        ----------
        gist_id : str
            Unique gist identifier called `id` available in Github API
            e.g. "MDQ6R2lzdGUzOTNkODgxMjIyODg1ZjU5ZWYwOWExNDExNzE1OWM4"

        Returns
        -------
        guid : str

        """
        return self.info.get(gist_id, {}).get('note_guid', '')


    def save_gist(self, gist):
        """Save information of a given gist into database.

        Parameters
        ----------
        gist : dict
            A Gist acquired by Github GraphQL API with format like:
                {
                    'id': 'gist_id',
                    'name': 'gist_name',
                    'description': 'description',
                    'pushAt': '2018-01-15T00:48:23Z',
                    'hash': 'hash value'
                }

        """
        self.info[gist['id']] = gist
        self.info['num_gists'] = self.info.get('num_gists', 0) + 1
        self.sync_info('save')
        self.update_sync_time()

    def update_gist(self, gist):
        """Update information of a given gist into database.

        Parameters
        ----------
        gist : dict
            A Gist acquired by Github GraphQL API with format like:
                {
                    'id': 'gist_id',
                    'name': 'gist_name',
                    'description': 'description',
                    'pushAt': '2018-01-15T00:48:23Z',
                    'hash': 'hash value'
                }

        """
        self.info[gist['id']] = gist
        self.sync_info('save')
        self.update_sync_time()

    def update_sync_time(self):
        """Update last synchronization time"""
        now = datetime.strftime(datetime.utcnow(), DATE_FORMAT)
        self.env['sync_at'] = now
        self.sync_env('save')

    def sync_env(self, mode):
        """Synchronize runtime information between current Database obj and permanent storage

        Parameters
        ----------
        mode : str
            Indicating to save or load environment. Valid values: ["save", "load"]

        Returns
        -------
        bool

        """
        if mode == 'save':
            with open(ENV_FILE, 'w') as fp:
                json.dump(self.env, fp, indent=2)
        elif mode == 'load':
            with open(ENV_FILE, "r") as fp:
                env = json.load(fp)
                self.env = env
        return True

    def sync_info(self, mode):
        """Synchronize gist info between current Database obj and permanent storage

        Parameters
        ----------
        mode : str
            Indicating to save or load environment. Valid values: ["save", "load"]

        Returns
        -------
        bool

        """
        if mode == 'save':
            with open(DB_FILE, 'w') as fp:
                json.dump(self.info, fp, indent=2)
        elif mode == 'load':
            with open(DB_FILE, "r") as fp:
                info = json.load(fp)
                self.info = info
        return True


def get_db():
    """Get a database instance for storing gist information

    Returns
    -------
    db : Database instance

    """
    return Database()


if __name__ == '__main__':
    fire.Fire()