import os
import json
import fire
from datetime import datetime
DB_FILE = 'db.json'
ENV_FILE = 'env.json'


class Database(object):
    """Storage class to keep track of gist sync information.

    This class is independent of the actual implementation
    of the database, thus make it easier to change in the future.
    """

    def __init__(self):
        if not os.path.isfile(DB_FILE):
            self.info = {}
            self.num_gists = 0
            self.cold_start = True
            return

        with open(DB_FILE, "r") as fp:
            self.info = json.load(fp)
            self.num_gists = len(self.info.keys())

        with open(ENV_FILE, "r") as fp:
            env = json.load(fp)
            self.cold_start = env['cold_start']

    def is_empty(self):
        """Indicate whether there is any gist in database.

        Returns
        -------
        bool

        """
        return self.num_gists == 0

    def start_from_scratch(self):
        """Indicate whether to synchronize all gists.

        Returns
        -------
        bool

        """
        return self.cold_start

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
        self.num_gists += 1
        with open(DB_FILE, 'w') as fp:
            json.dump(self.info, fp, indent=4)


def get_db():
    """Get a database instance for storing gist information

    Returns
    -------
    db : Database instance

    """
    return Database()


if __name__ == '__main__':
    fire.Fire()