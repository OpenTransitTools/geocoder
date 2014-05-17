import logging
log = logging.getLogger(__file__)

import solr
from ott.utils import object_utils
from ott.utils import json_utils
from ott.utils import html_utils
from .geo_dao  import GeoListDao, GeoDao

"""

THOUGHTS:

 1) need to return either 1 or many (ambiguous) hits from this service
 2) numFound="1" start="0" maxScore="12.307828   vs.  numFound="2209" start="0" maxScore="5.221347"
    stop_id:2  vs  2
 3) how to determine to send one result or many as ambiguous result by looking at relative scores between hit 1 and 2
    for the 2: "score"=5.221347 for the stop id 2, and the next highest "score"=1.1360569 for 2 NW 2ND AVE
 4)

"""

class GeoSolr(object):

    def __init__(self, url):
        self.solr_url = url
        self.solr_select = url + "/select"
        self.connection = solr.SolrConnection(url)
        log.debug("create an instance of {0}".format(self.__class__.__name__))

    def query(self, search, rows=10, start=0, qt="dismax"):
        """ call solr
            @see: http://maps.trimet.org/solr/select?rows=10&start=0&qt=dismax&q=x
        """
        ret_val = None
        ret_val = self.connection.query(search, rows=rows, start=start, qt=qt)
        return ret_val

    def geocode(self, search, rows=50):
        """ used for stop geocoder
        """
        gc = []
        if search:
            doc = self.query(search, rows)
            gc = self.filter_geo_result(doc)
        ret_val = GeoListDao(gc)
        return ret_val

    def make_geo(self, doc):
        ret_val = None
        name = html_utils.html_escape(doc['name'])
        lat  = doc['lat']
        lon  = doc['lon']
        ret_val = "{0}::{1},{2}".format(name, lat, lon)
        return ret_val


    @classmethod
    def filter_geo_result(cls, doc, limit=50, tolerance=0.5, include_city=False):
        ret_val = []
        if doc and doc.results and len(doc.results) > 0:
            top = doc.results[0]
            top_score = top['score']
            min_score = top_score * tolerance
            for d in doc.results:
                if d['score'] < min_score:
                    break
                g = GeoDao.make_geo_dao(d)
                ret_val.append(g)
        return ret_val


    def geostr(self, search, def_val="NOT FOUND::45.6,-122.65", rows=1):
        """ returns a geo string of the first SOLR hit, ala PLACE::45.5,-122.5
        """
        ret_val = def_val
        r = self.query(search, rows)
        if r and r.results:
            ret_val = self.make_geo(r.results[0])
        return ret_val


    def solr(self, search, rows=None, start=0, qt="dismax", pretty=False):
        """ call solr directly, and output the result
            TODO: this might be slower than it neeeds to be ... marshalling to py, then back out to json
        """
        ret_val = {}
        if rows is None:
            rows = '10'
        args = "q={0}&rows={1}&start={2}&qt={3}&wt=json".format(search, rows, start, qt)
        ret_val = json_utils.stream_json(self.solr_select, args)
        return ret_val


