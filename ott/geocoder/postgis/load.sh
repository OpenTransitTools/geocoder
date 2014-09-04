TMPDIR="/gisdata/temp/"
UNZIPTOOL=unzip
WGETTOOL="/usr/bin/wget"
export PGBIN=/opt/opengeo/pgsql/9.1/bin/
export PGPORT=5432
export PGHOST=localhost
export PGUSER=postgres
export PGPASSWORD=yourpasswordhere
export PGDATABASE=geocoder
PSQL=${PGBIN}/psql
SHP2PGSQL=${PGBIN}/shp2pgsql

wget http://www2.census.gov/geo/pvs/tiger2010st/41_Oregon/ --no-parent --relative --recursive --level=2 --accept=zip,txt --mirror --reject=html

#wget http://www2.census.gov/geo/pvs/tiger2010st/53_Washington/ --no-parent --relative --recursive --level=2 --accept=zip,txt --mirror --reject=html
