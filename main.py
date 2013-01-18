#! /usr/bin/env python

# main.py -- sample driver routine for the library
#
# Copyright (C) 2013 Satish BD  <bdsatish@gmail.com>
# Downloaded from https://github.com/bdsatish/drik-panchanga
# 
# This file is part of the "drik-panchanga" Python library
# for computing Hindu luni-solar calendar based on the Swiss ephemeris
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Sample driver routine
"""

from panchanga import *

def driver():
  print("Welcome to Drik Panchanga\n")
  date = raw_input("Enter date YYYY-MM-DD: ")
  year, month, day = map(int, date.split('-'))
  date = Date(year, month, day)
  place = raw_input("Enter place Latitude Longitude Timezone (eg: 12.972 77.594 +5.5): ")
  lat, lon, tz = map(float, place.split(' '))
  place = Place(lat, lon, tz)


if __name__ == "__main__":
  driver()
