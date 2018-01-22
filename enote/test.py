import time
import sys
import unittest
import util


class Test(unittest.TestCase):
    """ Test Evernote API"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_access(self):
        """Test simple access to Evernote API"""
        util.simple_access()

    def test_create_note(self):
        auth_token = util.get_auth_token()
        note_store = util.get_note_store()
        util.create_note(auth_token, note_store, 'Test Note', 'Hello world')

    def test_create_note_with_attachments(self):
        auth_token = util.get_auth_token()
        note_store = util.get_note_store()

        resources = []
        resource = util.create_resource('images/test.png')
        resources.append(resource)

        util.create_note(auth_token, note_store,
                         'Test Note with attachments', 'Hello world', resources)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
