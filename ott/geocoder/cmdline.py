import argparse
from .geosolr import GeoSolr

def init_parser():
    parser = argparse.ArgumentParser(
        prog='ott geocoder (wrapper)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'search',
        help='search term',
    )
    parser.add_argument(
        '--limit',
        '-l',
        default='10',
        help='limit search results to this many'
    )
    parser.add_argument(
        '--start',
        '-s',
        default='0',
        help='start index of the search'
    )
    parser.add_argument(
        '--url',
        '-u',
        default="http://maps.trimet.org/solr",
        help='SOLR Url',
    )
    args = parser.parse_args()
    return args


def main():
    #import pdb; pdb.set_trace()
    args = init_parser()
    geo = GeoSolr(args.url)
    r = geo.query(args.search, args.limit, args.start)
    for hit in r.results:
        print hit
        print
    
    print r

if __name__ == '__main__':
    main()
