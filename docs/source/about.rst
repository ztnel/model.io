=====
About
=====

Why *Myosin*?
-------------

*Myosin* is a lightweight framework for developing state-driven software systems. It provides a flexible and strictly-typed API for creating system state variables and a global thread-safe context manager for read and write access. State variables use an object-oriented data schemas to simplify access to state data and improving system scalability. This is a significant improvement over passing generic data structures to multiple system components because access to Python ``object`` data is customizable and self descriptive using ``properties``.

Core Features
-------------

Lightweight
~~~~~~~~~~~
Built using Python 3.7 core standard library. The small dependancy tree improves application security and robustness.

Fully Permissive
~~~~~~~~~~~~~~~~
The global state context manager allows for read and writes to the state models agnostic of your application's structure or implementation. The limited rule set gives more power to the application developer making *Myosin* a flexible choice for any system.

Fault-Tolerance
~~~~~~~~~~~~~~~
*Myosin* comes equipped with the option to write system state objects into persistant storage when a system state model is updated. If the application crashes and restarts, *Myosin* will load the previously cached system states properties recovering the system to its previously stable state. *Myosin* enforces all system state models are python objects with designated property getters and setters to enable custom validation on state model fields. If a system state model is set with an invalid value, the model can raise an exception before it is written to the system state.

Thread Safety
~~~~~~~~~~~~~
All system state accessors are fully thread-safe with mutexes for each model reducing latency for concurrent read and write operations. Access to state models are done using deep copies (pass by value) to decouple the local models from state managed models.

State-Driven Event Queue
~~~~~~~~~~~~~~~~~~~~~~~~
Support for state subscriber callback execution in response to a change to system state model.

Strictly Typed API
~~~~~~~~~~~~~~~~~~
All public methods for access and modification to system state variables are strictly typed for intellisense and static analysis tools like ``Pylance``, reducing development error feedback time.

.. note::
    It is highly encouraged that all state models are type hinted and include custom property getters and setters to fully leverage development tooling and fault-tolerance capabilities.

.. figure:: ../_static/typing.gif
    :align: center

Prometheus Monitoring
~~~~~~~~~~~~~~~~~~
*Myosin* uses the prometheus client python library to export performance metrics to a prometheus instance enabling real-time monitoring of your core application runtime and providing performance insights to aid system optimization and debugging.

