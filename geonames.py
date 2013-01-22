# Throw-away script for one-time use only.
#
# Generates a list of cities whose population is more than 50000
#
# Download cities15000.zip from http://download.geonames.org/export/dump/
#

import csv
import json

fin = open('/tmp/cities15000.txt', 'r')
reader = csv.reader(fin, 'excel-tab')
fout = open('/tmp/cities.csv', 'w')
cities = {}

for record in reader:
    (geonameid, name, asciiname, alternatenames, latitude, longitude,
     featureclass, featurecode, countrycode, cc2, admin1code,
     admin2code, admin3code, admin4code, population,
     elevation, dem, timezone, modificationdate) = record

    # Ignore small cities
    if int(population) > 50000 and asciiname:
      cities[asciiname] = {'latitude': float(latitude),
                           'longitude': float(longitude),
                           'timezone': timezone}
      fout.write(u'%s:%s:%s:%s\n' % (asciiname, latitude, longitude, timezone))

fout.close()
fjson = open('/tmp/cities.json', 'w')
json.dump(cities, fjson)
fjson.close()
