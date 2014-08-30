import logging
log = logging.getLogger(__file__)

import re
import solr
from ott.utils import object_utils
from ott.utils import json_utils
from ott.utils import html_utils
from ott.utils import geo_utils
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
        self.address_re = None
        log.debug("create an instance of {0}".format(self.__class__.__name__))

    def query(self, search, rows=10, start=0, qt="dismax", fq="(-type:26 AND -type:route)"):
        """ call solr
            @see: http://maps.trimet.org/solr/select?start=0&rows=10&qt=dismax&fq=(-type:26 AND -type:route)&q=zoo
        """
        #import pdb; pdb.set_trace()
        ret_val = None
        ret_val = self.connection.query(search, start=start, rows=rows, qt=qt, fq=fq)
        return ret_val

    def geocode(self, search, rows=50):
        """ used for stop geocoder
        """
        gc = []
        if search:
            recs = self.query(search, rows)
            gc = self.filter_geo_result(recs, search)
        ret_val = GeoListDao(gc)
        return ret_val

    @classmethod
    def similar_records(cls, rec1, rec2, dist_diff=0.01):
        ret_val = False
        if rec1 and rec2:
            if  object_utils.str_compare(rec1['name'], rec2['name']) \
            and object_utils.str_compare(rec1['city'], rec2['city']) \
            and object_utils.str_compare(rec1['lat'],  rec2['lat'])  \
            and object_utils.str_compare(rec1['lon'],  rec2['lon']):
                ret_val = True
        return ret_val


    def filter_geo_result(self, recs, search, limit=50, tolerance=0.5, include_city=False):
        ''' will filter out the geocoder results based on a handful of rules, like
             1) avoid duplicates
             2) match on exact name ... and avoid the rest
             3) look at the matching score, and filter out those hits that fall below a certain tolerance 
        '''
        ret_val = []
        if recs and recs.results and len(recs.results) > 0:
            #import pdb; pdb.set_trace()
            # step 0: get trimmed out name (and city) from the search string
            name, city = geo_utils.get_name_city_from_string(search)
            name = name.lower().strip() if name else search.lower().strip()
            city = city.lower().strip() if city else None

            # step 1: find a low score floor
            top = recs.results[0]
            top_score = top['score']
            min_score = top_score * tolerance

            # step 2: determine if our search string is all or part of the top result (see below in for loop)
            #         e.g., we might have 1 Main Street as a search string, so we want to return all hits for that exact match
            match_only   = False
            match_within = False
            if name == top['name'].strip().lower():
                match_only = True
            elif name in top['name'].strip().lower():
                match_within = True

            # step 3: set up the filter types (e.g., filter stops if we see a string like "[number]+ [compass direction]"
            filter_stops = False
            filter_zips  = False
            if self.is_address(search):
                filter_stops = True
                filter_zips  = True

            prev = None
            for d in recs.results:
                rec_name = d['name'].strip().lower()
                rec_city = None
                if d['city'] and len(d['city']) > 0:
                    rec_city = d['city'].strip().lower()

                # condition 1: filter types
                if filter_stops and d['type'] == 'stop':      continue
                if filter_zips  and d['type'] == 'zipcode':   continue

                # condition 2: matching exact strings (engaged when first result == record name) 
                if match_only and name != rec_name:
                    continue

                # condition 3: breaking after a certain hit score it seen
                if d['score'] < min_score:
                    break

                # condition 4: string partial match
                if match_within and name not in rec_name:
                    continue

                # condition 5: filter multiple records with same name/city (e.g., only one PDX in result) 
                if self.similar_records(prev, d):
                    continue

                # make the geocode record
                g = GeoDao.make_geo_dao(d)
                ret_val.append(g)
                prev = d

                # condition 5: break if we see the search string fully match the stop id
                if 'stop_id' in d and name == d['stop_id']:
                    break

                # condition 6: if we have both name and city, and they exactly match this record, let's just return this record...
                if name == rec_name and city == rec_city:
                    ret_val = []
                    ret_val.append(g)
                    break

        # further filters for when we get more than one exact match
        if len(ret_val) > 1:

            # condition 7: if we just have two address points, which are close by (e.g., intersections), just return one point
            if len(ret_val) == 2 and ret_val[0].type == 'address':
                a = ret_val[0]
                b = ret_val[1]
                if a.is_same_type(b) and a.is_nearby(b):
                    ret_val = []
                    ret_val.append(a)

        return ret_val


    def is_address(self, str):
        ''' does string look like an (US postal) address
        '''
        ret_val = None
        try:
            if self.address_re == None:
                self.address_re = re.compile("^[0-9]+[\s\w]+\s(north|south|east|west|n|s|e|w){1,2}(?=\s|$)", re.IGNORECASE)
            ret_val = self.address_re.search(str)
        except:
            self.address_re = None
        return ret_val


    def geostr(self, search, def_val="NOT FOUND::45.6,-122.65", rows=1):
        """ returns a geo string of the first SOLR hit, ala PLACE::45.5,-122.5
        """
        ret_val = def_val
        r = self.query(search, rows)
        if r and r.results:
            ret_val = geo_utils.solr_to_named_param(r.results[0])
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


