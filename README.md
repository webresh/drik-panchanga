Drik Panchanga
==============

Observational Indian lunisolar calendar using the Swiss ephemeris (Hindu 
Drig-ganita Panchanga).

Features
--------

Computation of the five essentials of the panchangam:
* Tithi
* Nakshatra
* Yoga
* Karana
* Vaara

Not just the values, but also the end times of tithis and nakshatras
are computed. The only factor limiting the accuracy of the program
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
The core of the library (`panchanga.py`) can be imported into other code
or used from the command line.

In order to just _run_ the GUI (`gui.py`) you also need python-tz and
wxPython (interface to wxWidgets):
```
    apt-get install python-tz
    apt-get install python-wxgtk2.8
```

If you want to _modify_ the GUI (`Gui.wxg`), you must use wxGlade:
```
    apt-get install python-wxglade
```

How does it look?

[Sample screenshot](http://s9.postimage.org/sag602wvz/screenshot.jpg):

![Sample screenshot](http://s9.postimage.org/sag602wvz/screenshot.jpg "Hindu Panchanga")


License
-------

GNU Affero GPL version 3.


#### TODO ####

* Festivals
* Rahukala, Yamaganda
