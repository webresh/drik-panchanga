#! /usr/bin/env python

# panchanga.py -- routines for computing tithi, vara, etc.
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
Use Swiss ephemeris to calculate tithi, nakshatra, etc.
"""

from __future__ import division
from math import floor, ceil
from collections import namedtuple as struct
import swisseph as swe

Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Location', ['latitude', 'longitude', 'timezone'])


# Convert 23d 30' 30" to 23.508333 degrees 
from_dms = lambda degs, mins, secs: degs + mins/60 + secs/3600

# the inverse
def to_dms(deg):
  d = int(deg)
  mins = (deg - d) * 60
  m = int(mins)
  s = int(round((mins - m) * 60))
  return [d, m, s]

def unwrap_angles(angles):
  """Add 360 to those elements in the input list so that
     all elements are sorted in ascending order."""
  result = angles
  for i in range(1, len(angles)):
    if result[i] < result[i-1]: result[i] += 360

  assert(result == sorted(result))
  return result

def inverse_lagrange(x, y, ya):
  """Given two lists x and y, find the value of x = xa when y = ya, i.e., f(xa) = ya"""
  assert(len(x) == len(y))
  total = 0
  for i in range(len(x)):
    numer = 1
    for j in range(len(x)):
      if j != i:  numer *= (ya - y[j])

    denom = 1
    for j in range(len(x)):
      if j != i:  denom *= (y[i] - y[j])

    total += numer * x[i] / denom

  return total

# Julian Day number as on (year, month, day) at 00:00 UTC
gregorian_to_jd = lambda date: swe.julday(date.year, date.month, date.day, 0.0)

def solar_longitude(jd):
  """Solar longitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.SUN, flag = swe.FLG_MOSEPH)  # 0 = ignore speed computations
  return data[0]   # in degrees

def lunar_longitude(jd):
  """Lunar longitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.MOON, flag = swe.FLG_MOSEPH)  # 0 = ignore speed computations
  return data[0]   # in degrees

def lunar_latitude(jd):
  """Lunar latitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.MOON, flag = swe.FLG_MOSEPH)  # 0 = ignore speed computations
  return data[1]   # in degrees

def sunrise(jd, place):
  """Sunrise when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((rise - jd) * 24 + tz)

def sunset(jd, place):
  """Sunset when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
  setting = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((setting - jd) * 24 + tz)

def moonrise(jd, place):
  """Moonrise when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((rise - jd) * 24 + tz)

def moonset(jd, place):
  """Moonset when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
  setting = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((setting - jd) * 24 + tz)

# Tithi doesn't depend on Ayanamsa
def tithi(jd, place):
  """Tithi at sunrise for given date and place. Also returns tithi's end time."""
  # 1. Find time of sunrise
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number

  # 2. Find tithi at this JDN
  solar_long = solar_longitude(rise)
  lunar_long = lunar_longitude(rise)
  moon_phase = (lunar_long - solar_long) % 360
  today = ceil(moon_phase / 12)
  degrees_left = today * 12 - moon_phase
   
  # 3. Compute longitudinal differences at intervals of 0.25 days from sunrise
  offsets = [0.25, 0.5, 0.75, 1.0]
  lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
  solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
  relative_motion = [ moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]

  # 4. Find end time by 4-point inverse Lagrange interpolation
  y = relative_motion
  x = offsets
  # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
  approx_end = inverse_lagrange(x, y, degrees_left)
  ends = (rise + approx_end -jd) * 24 + tz

  return [int(today), to_dms(ends)]


def nakshatra(jd, place):
  """Current nakshatra as of julian day (jd)
     1 = Asvini, 2 = Bharani, ..., 27 = Revati
  """
  swe.set_sid_mode(swe.SIDM_LAHIRI)   # Force Lahiri

  # 1. Find time of sunrise
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number

  # Swiss Ephemeris always gives Sayana. So subtract ayanamsa to get Nirayana
  offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
  longitudes = [ (lunar_longitude(jd + t) - swe.get_ayanamsa_ut(rise)) % 360 for t in offsets]

  # 2. Today's nakshatra is when offset = 0
  # There are 27 Nakshatras spanning 360 degrees
  nak = ceil(longitudes[0] * 27 / 360)

  # 3. Find end time by 5-point inverse Lagrange interpolation
  y = unwrap_angles(longitudes)
  x = map(lambda i: jd + i, offsets)
  approx_end = inverse_lagrange(x, y, nak * 360 / 27)
  ends = (approx_end - x[0]) * 24 + tz
  return [int(nak), to_dms(ends)]


def yoga(jd, place):
  """Yoga at given jd and place.
     1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
  """
  swe.set_sid_mode(swe.SIDM_LAHIRI)   # Force Lahiri
  # 1. Find time of sunrise
  lat, lon, tz = place
  result = swe.rise_trans(jd, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number
  next_jd = ceil(rise)
  frac_day_left = next_jd - rise

  # 2. Find the Nirayana longitudes and add them
  lunar_long = (lunar_longitude(rise) - swe.get_ayanamsa_ut(rise)) % 360
  solar_long = (solar_longitude(rise) - swe.get_ayanamsa_ut(rise)) % 360
  total = (lunar_long + solar_long) % 360
  # There are 27 Yogas spanning 360 degrees
  yog = ceil(total * 27 / 360)

  # 3. Find how many longitudes is there left to be swept
  degrees_left = (360 / 27) - total % (360 / 27)

  # 3. Compute longitudinal sums at intervals of 0.25 days from sunrise
  offsets = [0.25, 0.5, 0.75, 1.0]
  lunar_long_diff = [ (lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets ]
  solar_long_diff = [ (solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets ]
  total_motion = [ moon + sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff) ]

  # 4. Find end time by 4-point inverse Lagrange interpolation
  y = total_motion
  x = offsets
  # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
  approx_end = inverse_lagrange(x, y, degrees_left)
  ends = (rise + approx_end -jd) * 24 + tz

  return [int(yog), to_dms(ends)]


def vaara(jd):
  """Weekday for given Julian day. 0 = Sunday, 1 = Monday,..., 6 = Saturday"""
  return 1 + int(ceil(jd) % 7)


# ----- TESTS ------
def all_tests():
  bangalore = Place(12.972, 77.594, +5.5)
  shillong = Place(25.569, 91.883, +5.5)
  helsinki = Place(60.17, 24.935, +2.0)
  date1 = gregorian_to_jd(Date(2009, 7, 15))
  date2 = gregorian_to_jd(Date(2013, 1, 18))
  date3 = gregorian_to_jd(Date(1985, 6, 9))
  date4 = gregorian_to_jd(Date(2009, 6, 21))
  print(tithi(date1, bangalore))  # Expected: krishna ashtami (23), ends at 27:07:09
  print(tithi(date2, bangalore))  # Expected: Saptami, ends at 16:24:04
  print(tithi(date3, bangalore))  # Expected: Krishna Saptami, ends at 25:03:22
  print(moonrise(date2, bangalore)) # Expected: 11:28:06
  print(moonset(date2, bangalore))  # Expected: 24:12:48
  print(sunrise(date2, bangalore))  # Expected:  6:47:20
  print(sunset(date2, bangalore))   # Expected: 18:12:58 
  print(nakshatra(date1, bangalore))  # Expected: 27 (Revati), ends at 17:06:24
  print(nakshatra(date2, bangalore))  # Expected: 27 (Revati), ends at 19:22:54
  print(nakshatra(date3, bangalore))  # Expecred: 24 (Shatabhisha) ends at 26:32:36
  print(yoga(date3, bangalore))  # Expected: Vishkambha (1), ends at 22:59:38
  print(yoga(date2, bangalore))  # Expected: Siddha (21), ends at 29:10:40
  assert(vaara(date2) == 5)
  print(tithi(date2, helsinki))  # Expected: Shukla saptami until 12:54:04
  print(sunrise(date4, shillong))   # On this day, Nakshatra and Yoga are skipped!
  print(nakshatra(date4, shillong))

if __name__ == "__main__":
  all_tests()

