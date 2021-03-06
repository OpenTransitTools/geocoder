import unittest

from ott.geocoder.geosolr import GeoSolr
import json


class TestSolr(unittest.TestCase):
    def setUp(self):
        self.geo = GeoSolr("http://maps10.trimet.org/solr")

    def tearDown(self):
        pass

    def test_partial_string(self):
        j = self.geo.geocode("834 SE Lamb")
        s = j.to_json()
        self.assertEqual(j.status_code, 200)
        self.assertGreaterEqual(len(j.results), 2)
        self.assertRegexpMatches(s, "834 SE LAMBERT")
        self.assertRegexpMatches(s, "8347 SE LAMBERT")

    def test_exact_string(self):
        j = self.geo.geocode("834 SE Lambert")
        s = j.to_json()
        self.assertEqual(j.status_code, 200)
        self.assertEqual(len(j.results), 1)
        self.assertRegexpMatches(s, "834 SE LAMBERT")

    def test_latlon(self):
        j = self.geo.geocode("-122.5,45.5")
        s = j.to_json()
        self.assertEqual(j.status_code, 200)
        self.assertEqual(len(j.results), 1)
        self.assertRegexpMatches(s, "-122.5,45.5")

    def test_named_latlon(self):
        j = self.geo.geocode("THIS PLACE::-122.5,45.5")
        s = j.to_json()
        print(s)
        self.assertEqual(j.status_code, 200)
        self.assertEqual(len(j.results), 1)
        self.assertRegexpMatches(s, "THIS PLACE")

