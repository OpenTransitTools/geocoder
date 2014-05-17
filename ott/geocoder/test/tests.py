import unittest
import transaction

from pyramid import testing

from ..models import DBSession


class TestMyView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_solr(self):
        pass
        #self.assertEqual(info['one'].name, 'one')

