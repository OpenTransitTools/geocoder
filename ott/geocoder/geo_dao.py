import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao

from ott.utils import html_utils
from ott.utils import object_utils
from ott.utils import geo_utils

class GeoListDao(BaseDao):
    def __init__(self, results):
        super(GeoListDao, self).__init__()
        self.results = results

    @classmethod
    def make_geo_list_dao(cls, doc):
        res = []
        ret_val = GeoListDao(res)
        try:
            for r in doc['results']:
                g = GeoDao.make_geo_dao(r)
                res.append(g)
            pass
        except Exception, e:
            pass
        return ret_val


class GeoDao(BaseDao):
    def __init__(self, name, lat, lon, city, stop_id, type, type_name, score):
        super(GeoDao, self).__init__()
        log.debug("create an instance of {0}".format(self.__class__.__name__))
        self.name = html_utils.html_escape(name)
        self.city = html_utils.html_escape(city)
        self.lat  = html_utils.html_escape_num(lat)
        self.lon  = html_utils.html_escape_num(lon)
        self.stop_id = html_utils.html_escape_num(stop_id)
        self.type_name = html_utils.html_escape_num(type_name)
        self.type = type
        self.score = score

    @classmethod
    def make_geo_dao(cls, doc):
        name = doc['name']
        city = object_utils.safe_dict_val(doc, 'city', '').title()
        lat  = doc['lat']
        lon  = doc['lon']
        stop_id = object_utils.safe_dict_val(doc, 'stop_id')
        score = doc['score']

        # stupid ATIS override (e.g., "Stop ID {x}" in name, so look for that formatting) ...
        if " Stop ID " in name:
            type = 'stop'
            type_name = 'Stop ID'
        else:
            type = doc['type']
            type_name = doc['type_name']

        ret_val = GeoDao(name, lat, lon, city, stop_id, type, type_name, score)
        return ret_val

    @classmethod
    def make_geo_dao_from_named_str(cls, str):
        ''' take a string (like 'LAT,LON; NAME::LAT,LON; or NAME::LAT,LON::CITY) and return a dao
        '''
        doc = geo_utils.from_place_str(str)
        name = doc['name']
        lat  = doc['lat']
        lon  = doc['lon']
        city = doc['city']
        ret_val = GeoDao(name, lat, lon, city, None, 'place', 'Place', 100.0)

    def is_same_type(self, other_geo):
        ''' compares this Geo object vs another Geo object 
            sees whether their 'type' attributes match
        '''
        ret_val = False
        try:
            if self.type == other_geo.type:
                ret_val = True
        except:
            pass
        return ret_val

    def is_nearby(self, other_geo, decimal_diff=0.0015):
        ''' compares this Geo object vs another Geo object using the is_nearby util method 
            NOTE: default is 0.0015, which is about a city block of Lat,Lon mercator projection
        '''
        ret_val = False
        try:
            ret_val = geo_utils.is_nearby(self.lat, self.lon, other_geo.lat, other_geo.lon, decimal_diff)
        except:
            pass
        return ret_val
