=========
Changelog
=========

Version numbers are set using `Semantic Versioning <http://semver.org>`_.

1.0.2 (2013-07-30)
==================

Features added
--------------

Bugs fixed
-----------
* When used with ``xml`` from Python's standard library, the XML strings were
  constructed wrongly and were thus unparseable. Now this is manually checked
  when exporting to a string and corrected if necessary.

Other changes
-------------

1.0.1 (2013-06-20)
==================

Features added
--------------

Bugs fixed
----------
* Pretty printed string representation of object is returned correctly without
  reliance on postprocessing in subclasses

Other changes
-------------

1.0.0 (2013-06-19)
==================

Features added
--------------
* Class ``XML`` allows defining a class with a predefined possible XML structure
  and setting tag names, attributes, values, etc. without the user having to
  know this structure. Output is valid, parseable XML.

Bugs fixed
----------

Other changes
-------------
