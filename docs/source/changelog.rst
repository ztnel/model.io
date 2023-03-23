*********
Changelog
*********

0.2b2
======

Fixed
-----
* ``StateModel`` subscriber callbacks can now be invoked in threads with an active ``asyncio`` event loop (`#63`_)

Changed
-------
* Bumped packaged ``prometheus-client`` to ``0.16.0`` (`#63`_)

.. _#63: https://github.com/ztnel/myosin/pull/63

0.2b1
======

New Features
------------
* Follow `PEP 440`_ versioning scheme
* Cleanup type hinting and improve API documentation (`#52`_)
* Added ``StateModel`` base class to the API documentation (`#52`_)
* Added myosin type aliases to the API documentation (`#52`_)

.. _#52: https://github.com/ztnel/myosin/pull/52
.. _PEP 440: https://peps.python.org/pep-0440/

Fixed
-----
* Raise ``ModelNotFound`` if ``State`` object is initialized with an unregistered StateModel (`#52`_)

.. _#52: https://github.com/ztnel/myosin/pull/52

Removed
-------
* ``BaseModel`` base class for ``StateModel`` abstractions


0.2.0
=====

New Features
------------
* Start of changelog
* State model level mutex locks to improve state access latency (`#42`_)
* Prometheus monitoring metrics (`#44`_)
* Updated API, Usage and About documentation pages

.. _#44: https://github.com/ztnel/myosin/pull/44
.. _#42: https://github.com/ztnel/myosin/pull/42

Fixed
-----
* API Exception documentation

Removed
-------
* ``NullCheckoutError`` and ``HashNotFound`` exceptions
