geocoder
========
@see http://opentransittools.com

build:
  1. install python 2.7, along with zc.buildout and easy_install, git
  2. git clone https://github.com/OpenTransitTools/geocoder.git
  2. cd geocoder
  3. buildout
  4. git update-index --assume-unchanged .pydevproject

run:
  1. bin/pserve config/pyramid.ini --reload
  2. http://localhost:35553/

test:
  1. bin/nosetests --exe -v
  2. Selenium Test: ott/geocoder/test/pages.html
  3. Selenium Test: ott/geocoder/test/services.html 
     @see Selenium IDE (Firefox Mac/Win) at http://docs.seleniumhq.org/projects/ide/ 

