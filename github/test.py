import time
import sys
import unittest
import util


class Test(unittest.TestCase):
    """ Test Github GraphQL API"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_access(self):
        """Test simple access to Github GraphQL API"""
        pass

        query = "{\"query\":\"query {\\n  viewer {\\n    login\\n  }\\n}\"}"
        print(util.query_graphql(query))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
