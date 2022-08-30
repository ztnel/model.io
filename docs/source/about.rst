=====
About
=====

State-Driven Design
-------------------

*Myosin* is a lightweight framework for developing state-driven software systems. It provides a flexible and strictly-typed API for creating system state variables and a global thread-safe context manager for read and write access. State variables use object-oriented data schemas to simplify access to state data and improving system scalability. This is a significant improvement over passing generic data structures to multiple system components because access to Python ``object`` data is customizable and self descriptive using ``properties``.

Core Features
-------------

Lightweight
~~~~~~~~~~~
Built using Python 3.7 standard library. The small dependancy tree improves application security and robustness.

Flexible
~~~~~~~~
The global state context manager handles synchronized and thread-safe reads and writes agnostic of your application's structure or implementation. Simply import ``State`` from any module to gain access to the system state. This makes *Myosin* a flexible for implementation in a variety of systems such as closed-loop embedded control systems to cloud data proxies.

Fault-Tolerance
~~~~~~~~~~~~~~~
*Myosin* has the ability to optionally write system state objects into persistant storage in response to a state model change. If the parent application crashes and restarts, *Myosin* will load the previously cached system states properties recovering the system to its previous state. *Myosin* also enforces that state models are python objects with designated property getters and setters. Developers can define rules for data validation on any number of state model property setters. During runtime, if a state model is set with an invalid value, *myosin* will catch and reraise the validation exception before the model is written to the system state reducing system faults.

Thread Safety
~~~~~~~~~~~~~
All system state accessors are fully thread-safe with mutexes for each shared resource, which in our case is represented as a state model. Mutex management for each registered resource reduces latency for concurrent read and write operations. Furthermore, state model reads are done using deep copies (pass by value) to decouple the local models from state managed models. Local edits of the model will not cause unintented upstream changes.

Asynchronous Event Queue
~~~~~~~~~~~~~~~~~~~~~~~~~
State subscriber callback execution is supported in response to a change to state model.

Strictly Typed API
~~~~~~~~~~~~~~~~~~
All public methods for access and modification to system state variables are strictly typed for static analysis tools such as *IntelliSense* and *Pylance*, reducing feedback time for errors in development.

.. note::
    It is highly encouraged that all state models are type hinted and include custom property getters and setters to fully leverage development tooling and fault-tolerance capabilities.

.. figure:: ../_static/typing.gif
    :align: center
    Pylance type hint semantic highlighting on custom Myosin state model 


Prometheus Monitoring
~~~~~~~~~~~~~~~~~~~~~
*Myosin* uses the prometheus client python library to export performance metrics to a prometheus instance enabling real-time monitoring of your core application runtime and providing performance insights to aid system optimization and debugging.

