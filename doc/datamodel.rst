==========
Data model
==========

Their is some hidden logic expressed that isn't obvious from the database schema.

* Various DB values (integers) map to array indices in the PHP website. These have been
  defined in ``pta_export.core.constants``.

* In the table exports, there are some dynamic columns, such as "weging ed4". ED4, ED5
  and ED6 map to the "leerjaar". For VWO 4 and HAVO 4, only ed4 is displayed, and
  similarly for other "leerjaren".

* The table marks some week numbers as ``(tw)`` - you can look up that week number in
  the matching calendar record to see if it's in ``tw11``, ``tw12``, ``tw21``, ``tw22``,
  ``tw31``, ``tw32``, ``tw41`` or ``tw42``. These mark which week numbers are
  "toetsweek".

* input: year & klas -> output: all vakken
