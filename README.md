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

NOTE:
All timings are end timings. Timings displayed higher than 24:00 denote
hours past midnight because the Hindu day (tithi) starts and ends with
sunrise. If applicable, daylight savings (DST) are accounted for
automatically based on the date and place entered in the textboxes.


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

[Sample screenshot](https://raw.githubusercontent.com/bdsatish/drik-panchanga/master/screenshot.jpg):

![Sample screenshot](https://raw.githubusercontent.com/bdsatish/drik-panchanga/master/screenshot.jpg "Hindu Panchanga")

Using the GUI
-------------

### Location known

First, type the Date in DD/MM/YYYY format in the 'Date' field. Negative value for YYYY are
interpolated as proleptic Gregorian calendar.

Second, type your location (city or district) in the Location field and click 'Search'.  If found,
then the coordinates and time zone are updated. If not, try the [next method](#location-unknown).
If your location's population is more than 50,000 then the location should be found.

Third, click 'Compute'. Now the fields like tithi, etc. are computed and shown on the GUI.

### Location unknown

First, type the Date in DD/MM/YYYY format in the 'Date' field.

Second, manually enter the coordinates and time zone of your location. You can use
[Google Maps](http://maps.google.com) or [Time and Date website](http://www.timeanddate.com/) for
this purpose.

Third, click 'Compute'.  Now the fields like tithi, etc. are computed and shown on the GUI.


Accuracy
--------

The program is as accurate as the Swiss Ephemeris installed on your system. So generally it is
accurate for years 5000 BCE to 5000 CE, especially in the range 2500 BCE - 2500 CE. The
computational speed stays the same no matter which date you enter. Compared to other software listed
in the [References](#references), our software is way better in this sense.

As a simple test, try to compute the date of Madhva Navami, which is celebrated as the disappearance
day of the Indian philosopher [Madhvācārya](http://en.wikipedia.org/wiki/Madhvacharya). The exact
date is 1317 CE, Māgha-māsa śukla-pakṣa navamī. All other software listed in
[References](#references) give error "Year out-of-range".  But in our software, enter the place
"Udipi" and date "30/1/1317" and you indeed get Māgha śuddha navamī. You can cross-verify it on the
[Calendrica website](http://emr.cs.iit.edu/home/reingold/calendar-book/Calendrica.html).

Note that dates before 1582 must be entered in
[proleptic Gregorian](https://en.wikipedia.org/wiki/Proleptic_Gregorian_calendar), which is a
natural back-interpolation of the current Gregorian calendar we use everyday.


About the calendar
------------------

There are two schools of Indian calendar makers:

1. Those who follow the rules of the [_Sūrya Siddhāntā_](http://en.wikipedia.org/wiki/Surya_Siddhanta)
   (SS, Theory of the Sun) or its variants like _Ārya Siddhānta_ of Aryabhata.
2. Those who follow the _Dṛk Siddhāntā_ (Empirical Theory).

SS contains semi-analytical equations for specifying the positions of sun and moon.
However, the constants in these equations have to be updated regularly ( _bīja saṃskāra_ ).
But the equations in SS were last updated around 1000 CE, so they no longer match the
planetary positions as we see today. For example, the date of solar eclipse as predicted
by the equations of SS are off by many hours from its actual occurence. In spite of this,
most Hindu maṭhas still publish yearly pañcāṅgas according to the rules of SS, in the name
of preserving and practising tradition ( _paramparā_ ).

The latter one, _Drik_ school, still follow the general concepts from SS,
but get the planetary positions from measured or observed data (dṛś = to see).
Hence, their results match accurately with observed celestial phenomena.
The [Swiss Ephemeris](http://www.astro.com/swisseph/swephinfo_e.htm) is probably
the best source available today for planetary calculations. It provides highly
accurate databases of planetary data for about 10000 years. Hence, this panchanga
is based on the Swiss Ephemeris. Other databases include those published by NASA's
JPL (DE405) or the Moshier ephemeris.


References
----------

These ones are helpful for implementing panchanga software:
* Karanam Ramakumar, [_Panchangam Calculations_](http://archive.org/details/PanchangamCalculations)
* _Second Level of the Astronomical Calculations in GCAL_, used in ISKCON's GCal software.

This is _the_ calendar book (though it mostly deals with Surya Siddhanta):
* Dershowitz and Reingold, _Calendrical Calculations_, 3rd edition, 2008.
  [Online Java applet](http://emr.cs.iit.edu/home/reingold/calendar-book/Calendrica.html).

#### Similar software ####

Prof. M. Yanom's [online interface](http://www.cc.kyoto-su.ac.jp/~yanom/pancanga/)
to his [Perl code](http://www.cc.kyoto-su.ac.jp/~yanom/sanskrit/pancanga/pancanga3.13) -- this
is the best version of the old Surya Siddhanta pancanga I've seen. However, the Surya Siddhanta
system (no fault with the Perl code) is not accurate if you want to work with dates which are
several centuries before our current time.

[drikpanchang](http://drikpanchang.com) is a reliable online calendar for the Drik.  However, it is
neither open source nor do they have a desktop program. This website doesn't work for dates before
1600 CE. Their [Android app](https://play.google.com/store/apps/details?id=com.drikp.core) doesn't
work for dates outside the range 1900 - 2100 CE.


[Hindu Calendar](https://play.google.com/store/apps/details?id=com.alokmandavgane.hinducalendar)
for Android is another offline Drik calendar by Alok Mandavgane. Again, this is
not open source. This software has a bug that it doesn't account for daylight savings
in Europe. Also it doesn't work for dates outside the range 1900 - 2100 CE.

Among open source programs, I found these two:

* [On Google Code](http://panchangam.googlecode.com/svn/calc-v2): generates a pdf of
panchanga for any year and place, but imprecise. For ex., tithi end timings are off
by ten minutes sometimes. There is no GUI either.

* [On GitHub](https://github.com/santhoshn/panchanga): Based on Paul Schlyter's
semi-analytical model for [planetary positions](http://stjarnhimlen.se/comp/ppcomp.html).
This program gives the panchanga for a given _instant_ but doesn't ask for a place's
coordinates or timezone. This is probably because the program doesn't compute sunrise
timings at all! The planetary model fails for dates outside the range 1800 CE to 2100 CE.


License
-------

GNU Affero GPL version 3 (or later).


#### TODO ####

* Festivals
* Rahukaala, Yamaganda kaala
