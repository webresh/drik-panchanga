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
    denom = 1
    for j in range(len(x)):
      if j != i:
        numer *= (ya - y[j])
        denom *= (y[i] - y[j])

    total += numer * x[i] / denom

  return total

# Julian Day number as on (year, month, day) at 00:00 UTC
gregorian_to_jd = lambda date: swe.julday(date.year, date.month, date.day, 0.0)

def solar_longitude(jd):
  """Solar longitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.SUN, flag = swe.FLG_SWIEPH)
  return data[0]   # in degrees

def lunar_longitude(jd):
  """Lunar longitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.MOON, flag = swe.FLG_SWIEPH)
  return data[0]   # in degrees

def lunar_latitude(jd):
  """Lunar latitude at given instant (julian day) jd"""
  data = swe.calc_ut(jd, swe.MOON, flag = swe.FLG_SWIEPH)
  return data[1]   # in degrees

def sunrise(jd, place):
  """Sunrise when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number
  # Convert to local time
  return [rise + tz/24., to_dms((rise - jd) * 24 + tz)]

def sunset(jd, place):
  """Sunset when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd - tz/24, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
  setting = result[1][0]  # julian-day number
  # Convert to local time
  return [setting + tz/24., to_dms((setting - jd) * 24 + tz)]

def moonrise(jd, place):
  """Moonrise when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd - tz/24, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
  rise = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((rise - jd) * 24 + tz)

def moonset(jd, place):
  """Moonset when centre of disc is at horizon for given date and place"""
  lat, lon, tz = place
  result = swe.rise_trans(jd - tz/24, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
  setting = result[1][0]  # julian-day number
  # Convert to local time
  return to_dms((setting - jd) * 24 + tz)

# Tithi doesn't depend on Ayanamsa
def tithi(jd, place):
  """Tithi at sunrise for given date and place. Also returns tithi's end time."""
  tz = place.timezone
  # 1. Find time of sunrise
  rise = sunrise(jd, place)[0] - tz / 24
  
  # 2. Find tithi at this JDN
  moon_phase = lunar_phase(rise)
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
  answer = [int(today), to_dms(ends)]

  # 5. Check for skipped tithi
  moon_phase_tmrw = lunar_phase(rise + 1)
  tomorrow = ceil(moon_phase_tmrw / 12)
  isSkipped = (tomorrow - today) % 30 > 1
  if isSkipped:
    # interpolate again with same (x,y)
    leap_tithi = today + 1
    degrees_left = leap_tithi * 12 - moon_phase
    approx_end = inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end -jd) * 24 + place.timezone
    answer += [int(leap_tithi), to_dms(ends)]

  return answer


def nakshatra(jd, place):
  """Current nakshatra as of julian day (jd)
     1 = Asvini, 2 = Bharani, ..., 27 = Revati
  """
  swe.set_sid_mode(swe.SIDM_LAHIRI)
  # 1. Find time of sunrise
  lat, lon, tz = place
  rise = sunrise(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00
   
  # Swiss Ephemeris always gives Sayana. So subtract ayanamsa to get Nirayana
  offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
  longitudes = [ (lunar_longitude(rise + t) - swe.get_ayanamsa_ut(rise)) % 360 for t in offsets]

  # 2. Today's nakshatra is when offset = 0
  # There are 27 Nakshatras spanning 360 degrees
  nak = ceil(longitudes[0] * 27 / 360)
  
  # 3. Find end time by 5-point inverse Lagrange interpolation
  y = unwrap_angles(longitudes)
  x = offsets
  approx_end = inverse_lagrange(x, y, nak * 360 / 27)
  ends = (rise - jd + approx_end) * 24 + tz
  answer = [int(nak), to_dms(ends)]

  # 4. Check for skipped nakshatra
  nak_tmrw = ceil(longitudes[-1] * 27 / 360)
  isSkipped = (nak_tmrw - nak) % 27 > 1
  if isSkipped:
    leap_nak = nak + 1
    approx_end = inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
    ends = (rise - jd + approx_end) * 24 + tz
    answer += [int(leap_nak), to_dms(ends)]

  return answer


def yoga(jd, place):
  """Yoga at given jd and place.
     1 = Vishkambha, 2 = Priti, ..., 27 = Vaidhrti
  """
  swe.set_sid_mode(swe.SIDM_LAHIRI)
  # 1. Find time of sunrise
  lat, lon, tz = place
  rise = sunrise(jd, place)[0] - tz / 24.  # Sunrise at UT 00:00

  # 2. Find the Nirayana longitudes and add them
  lunar_long = (lunar_longitude(rise) - swe.get_ayanamsa_ut(rise)) % 360
  solar_long = (solar_longitude(rise) - swe.get_ayanamsa_ut(rise)) % 360
  total = (lunar_long + solar_long) % 360
  # There are 27 Yogas spanning 360 degrees
  yog = ceil(total * 27 / 360)

  # 3. Find how many longitudes is there left to be swept
  degrees_left = yog * (360 / 27) - total

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
  ends = (rise + approx_end - jd) * 24 + tz
  answer = [int(yog), to_dms(ends)]

  # 5. Check for skipped yoga
  lunar_long_tmrw = (lunar_longitude(rise + 1) - swe.get_ayanamsa_ut(rise + 1)) % 360
  solar_long_tmrw = (solar_longitude(rise + 1) - swe.get_ayanamsa_ut(rise + 1)) % 360
  total_tmrw = (lunar_long_tmrw + solar_long_tmrw) % 360
  tomorrow = ceil(total_tmrw * 27 / 360)
  isSkipped = (tomorrow - yog) % 27 > 1
  if isSkipped:
    # interpolate again with same (x,y)
    leap_yog = yog + 1
    degrees_left = leap_yog * (360 / 27) - total
    approx_end = inverse_lagrange(x, y, degrees_left)
    ends = (rise + approx_end - jd) * 24 + tz
    answer += [int(leap_yog), to_dms(ends)]

  return answer


def karana(jd, place):
  """Returns the karana and their ending times. (from 1 to 60)"""
  # 1. Find time of sunrise
  rise = sunrise(jd, place)[0]

  # 2. Find karana at this JDN
  solar_long = solar_longitude(rise)
  lunar_long = lunar_longitude(rise)
  moon_phase = (lunar_long - solar_long) % 360
  today = ceil(moon_phase / 6)
  degrees_left = today * 6 - moon_phase

  return [int(today)]

def vaara(jd):
  """Weekday for given Julian day. 0 = Sunday, 1 = Monday,..., 6 = Saturday"""
  return int(ceil(jd + 1) % 7)

def masa(jd, place):
  """Returns lunar month and if it is adhika or not.
     1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna"""
  ti = tithi(jd, place)[0]
  critical = sunrise(jd, place)[0]  # - tz/24 ?
  last_new_moon = new_moon(critical, ti, -1)
  next_new_moon = new_moon(critical, ti, +1)
  this_solar_month = raasi(last_new_moon)
  next_solar_month = raasi(next_new_moon)
  is_leap_month = (this_solar_month == next_solar_month)
  maasa = this_solar_month + 1
  if maasa > 12: maasa = (maasa % 12)
  return [int(maasa), is_leap_month]

# epoch-midnight to given midnight
# Days elapsed since beginning of Kali Yuga
ahargana = lambda jd: jd - 588465.5

def elapsed_year(jd):
  swe.set_sid_mode(swe.SIDM_LAHIRI)
  ahar = ahargana(jd)
  mean_sidereal_year = 365.25636
  solar_long = (solar_longitude(jd) - swe.get_ayanamsa_ut(jd)) % 360
  kali = round(ahar / mean_sidereal_year -  solar_long / 360)
  saka = kali - 3179
  vikrama = saka + 135
  return kali, saka

# New moon day: sun and moon have same longitude (0 degrees = 360 degrees difference)
# Full moon day: sun and moon are 180 deg apart
def new_moon(jd, tithi_, opt = -1):
  """Returns JDN, where
     opt = -1:  JDN < jd such that lunar_phase(JDN) = 360 degrees
     opt = +1:  JDN >= jd such that lunar_phase(JDN) = 360 degrees
  """
  if opt == -1:  start = jd - tithi_         # previous new moon
  if opt == +1:  start = jd + (30 - tithi_)  # next new moon
  # Search within a span of (start +- 2) days
  x = [ -2 + offset/4 for offset in range(17) ]
  y = [lunar_phase(start + i) for i in x]
  y = unwrap_angles(y)
  y0 = inverse_lagrange(x, y, 360)
  return start + y0

def raasi(jd):
  """Zodiac of given jd. 1 = Mesha, ... 12 = Meena"""
  swe.set_sid_mode(swe.SIDM_LAHIRI)
  s = solar_longitude(jd)
  solar_nirayana = (solar_longitude(jd) - swe.get_ayanamsa_ut(jd)) % 360
  # 12 rasis occupy 360 degrees, so each one is 30 degrees
  return ceil(solar_nirayana / 30.)

def lunar_phase(jd):
  solar_long = solar_longitude(jd)
  lunar_long = lunar_longitude(jd)
  moon_phase = (lunar_long - solar_long) % 360
  return moon_phase

def samvatsara(jd):
  ahar = ahargana(jd)
  jupiter_period = 1577917500 / 364224  # number of days for revolution around sun
  # Change 13 to 27 (14 yrs offset) for North Indian tradition
  # See the function "get_Jovian_Year_name_south" in pancanga.pl
  samvat = (int(ahar / (jupiter_period / 12)) + 13) % 60
  return samvat

def ritu(masa_num):
  """0 = Vasanta,...,5 = Shishira"""
  return (masa_num - 1) // 2

def day_duration(jd, place):
  srise = sunrise(jd, place)[0]  # julian day num
  sset = sunset(jd, place)[0]    # julian day num
  diff = (sset - srise) * 24     # In hours
  return [diff, to_dms(diff)]

# ----- TESTS ------
def all_tests():
  print(moonrise(date2, bangalore)) # Expected: 11:28:06
  print(moonset(date2, bangalore))  # Expected: 24:12:48
  print(sunrise(date2, bangalore)[1])  # Expected:  6:47:20
  print(sunset(date2, bangalore)[1])   # Expected: 18:12:58 
  assert(vaara(date2) == 5)
  print(sunrise(date4, shillong)[1])   # On this day, Nakshatra and Yoga are skipped!
  assert(karana(date2, helsinki) == [14])   # Expected: 14, Vanija
  return

def tithi_tests():
  feb3 = gregorian_to_jd(Date(2013, 2, 3))
  apr24 = gregorian_to_jd(Date(2010, 4, 24))
  apr19 = gregorian_to_jd(Date(2013, 4, 19))
  apr20 = gregorian_to_jd(Date(2013, 4, 20))
  apr21 = gregorian_to_jd(Date(2013, 4, 21))
  print(tithi(date1, bangalore))  # Expected: krishna ashtami (23), ends at 27:07:09
  print(tithi(date2, bangalore))  # Expected: Saptami, ends at 16:24:04
  print(tithi(date3, bangalore))  # Expected: Krishna Saptami, ends at 25:03:22
  print(tithi(date2, helsinki))   # Expected: Shukla saptami until 12:54:04
  print(tithi(apr24, bangalore))  # Expected: [10, [6,9,18], 11, [27, 33, 50]]
  print(tithi(feb3, bangalore))   # Expected: [22, [8,13,52], 23, [30, 33, 6]]
  print(tithi(apr19, helsinki))   # Expected: [9, [28, 44, 60]]
  print(tithi(apr20, helsinki))   # Expected: [10, - ahoratra -]
  print(tithi(apr21, helsinki))   # Expected: [10, [5, 22, 6]]
  return

def nakshatra_tests():
  print(nakshatra(date1, bangalore))  # Expected: 27 (Revati), ends at 17:06:24
  print(nakshatra(date2, bangalore))  # Expected: 27 (Revati), ends at 19:22:54
  print(nakshatra(date3, bangalore))  # Expecred: 24 (Shatabhisha) ends at 26:32:36
  print(nakshatra(date4, shillong))   # Expected: [3, [5,0,59]] then [4,[26,31,00]]
  return

def yoga_tests():
  may22 = gregorian_to_jd(Date(2013, 5, 22))
  print(yoga(date3, bangalore))  # Expected: Vishkambha (1), ends at 22:59:38
  print(yoga(date2, bangalore))  # Expected: Siddha (21), ends at 29:10:40
  print(yoga(may22, helsinki))   # [16, [6,20,25], 17, [27,21,53]]

def masa_tests():
  jd = gregorian_to_jd(Date(2013, 2, 10))
  aug17 = gregorian_to_jd(Date(2012, 8, 17))
  aug18 = gregorian_to_jd(Date(2012, 8, 18))
  sep19 = gregorian_to_jd(Date(2012, 9, 18))
  may20 = gregorian_to_jd(Date(2012, 5, 20))
  may21 = gregorian_to_jd(Date(2012, 5, 21))
  print(masa(jd, bangalore))     # Pusya (10)
  print(masa(aug17, bangalore))  # Shravana (5) amavasya
  print(masa(aug18, bangalore))  # Adhika Bhadrapada [6, True]
  print(masa(sep19, bangalore))  # Normal Bhadrapada [6, False]
  print(masa(may20, helsinki))   # Vaisakha [2]
  print(masa(may21, helsinki))   # Jyestha [3]

if __name__ == "__main__":
  bangalore = Place(12.972, 77.594, +5.5)
  shillong = Place(25.569, 91.883, +5.5)
  helsinki = Place(60.17, 24.935, +2.0)
  date1 = gregorian_to_jd(Date(2009, 7, 15))
  date2 = gregorian_to_jd(Date(2013, 1, 18))
  date3 = gregorian_to_jd(Date(1985, 6, 9))
  date4 = gregorian_to_jd(Date(2009, 6, 21))
  apr_8 = gregorian_to_jd(Date(2010, 4, 8))
  apr_10 = gregorian_to_jd(Date(2010, 4, 10))
  # all_tests()
  # tithi_tests()
  # nakshatra_tests()
  # yoga_tests()
  masa_tests()
  # new_moon(jd)

