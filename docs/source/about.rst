=====
About
=====

Why *Myosin*?
-------------

*Myosin* is a lightweight framework for developing state-driven software systems. It provides a flexible and strictly-typed API for creating system state variables and a global thread-safe context manager for read and write access. *Myosin* state variables use an object-oriented data schemas to simplify access to state data and improving system scalability. This is a significant improvement over passing generic data structures to multiple system components because access to Python ``object`` data is customizable and self descriptive using ``properties``.

Core Features
-------------

Fault-Tolerance
~~~~~~~~~~~~~~~
*Myosin* comes equipped with the option to write system state objects into persistant storage when a system state model is updated. If the application crashes and restarts, *Myosin* will load the previously cached system states properties recovering the system to its previously stable state.

*Myosin* enforces all system state models are python objects with designated property getters and setters to enable custom validation on state model fields. If a system state model is set with an invalid value, the model can raise an exception before it is written to the system state.

Fully Permissive
~~~~~~~~~~~~~~~~
Any software component can access and write to system state models agnostic of your projects hierarchical structure. Import the ``State`` context manager from anywhere to gain access to the systems state models.

Thread Safety
~~~~~~~~~~~~~
All system state accessors are fully thread-safe and support concurrent read and write operations. Access to *myosin* state models are done using the deep copies (pass by value) of the source state model so local modification can be done safely.

Lightweight
~~~~~~~~~~~
*Myosin* is built using python's standard library from 3.7 onwards. The combination of a small dependancy tree and simple implementation improves application security and resiliency.

State-Driven Event Queue
~~~~~~~~~~~~~~~~~~~~~~~~
*Myosin* supports state subscriber callbacks to be scheduled in response to a change to a specific system state. Callbacks must be asynchronous and accept a single parameter for the new system state subscribed to by the callback.

Strictly Typed API
~~~~~~~~~~~~~~~~~~
All *myosin* functions for access and modification to system state variables are strictly typed for intellisense and static type analysis tools like ``Pylance`` making the programming with *myosin* easy and error-free. Type accuracy for state models are left to the developer. It is highly encouraged that all state models loaded into *myosin* are strictly typed with property getters and setters for each field to leverage the full typing capabilities.

.. image:: ../_static/typing.gif
    :align: center


