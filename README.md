Drik Panchanga
==============

Empirical Indian lunisolar calendar using the Swiss ephemeris (Hindu Drik Panchanga).

Features
--------

Computation of the five essentials of the panchangam:
* Tithi
* Nakshatra
* Yoga
* Karana
* Vaara

Not just the values, but also the end times of tithis and nakshatras
are computed as well. The only factor limiting the accuracy of the program
output is the uncertainity in your input values (latitude, longitude). 

Also includes computation of sunrise, sunset, moonrise and moonset.

By default, the month type is Amavasyanta (new moon to new moon) which
is most prominent type of calendar used in South India.

Requirements
------------

Python interface to Swiss ephemeris.
```
     pip install pyswisseph  # OR apt-get install pyswisseph
```

License
-------

GNU Affero GPL version 3.


