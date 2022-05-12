=====
About
=====

Myosin is a lightweight state management framework for developing state-driven software systems. The term describes a biological motor protein which converts chemical energy into mechanical energy.

Why Myosin?
-----------

State-driven systems are useful for allowing multiple software components within an application to communicate using the same language. The syntax for communication of data is implemented through the state models which are object-oriented representations of the system state.

Traditionally, embedded systems use `event-driven architectures <https://en.wikipedia.org/wiki/Event-driven_architecture>`_ for synchronizing state changes across multiple software components. Event driven solutions, while simple to implement do not scale well for handling bidirectional data transfer with multiple contexts.

For example, imagine we have an embedded system with three software components. A UART Interface for communicating with an embedded firmware device, a Cloud Link component for providing a real-time data stream to a cloud service and a User Interface Controller for updating an embedded GUI. 

.. image:: ../_static/event.png
    :align: center

The Cloud Link and User Interface operate with their own control loops and digest new sensorframe payloads through the SENSORFRAME event dispatched by the UART Interface. In order to provide real-time telemetric updates both the Cloud Link and User Interface store previously cached sensorframe payloads and update their values when a SENSORFRAME event is received and a delta is detected between any of the sensorframe keys. In this model, state data is duplicated and can be out of sync across components. Data integrity is compromised as there is no source of truth for sensorframe updates except by the most recent event payload. If the event payload is implemented as a dictionary then unpacking of event payloads is also duplicated across components and not reusable across different event payloads.


Myosin acts as a datastore system state models. A state model (Sensorframe) is registered and loaded into myosin as a python object on boot. This object holds properties describing the state. As the UART Interface updates the system with a new sensorframe reading it commits a new sensorframe instance to myosin. The advantage of this is that a state has a source of truth. Each module with a control loop can simply poll the state from myosin checking out a copy of the active state model. The major benefit in this architecture is the consistent universal access to system state variables. Each property in a python object can have custom typing and validation checks. Any access rules implemented at the property level are universal to any component accessing that state property.

.. image:: ../_static/state.png
    :align: center


Events are inherently contextless and therefore more events are required for different contexts increasing the complexity of the system. real-time cloud service and a REST API. Every endpoint made on the device locally required a synchronous cloud update event and vice-versa. Tight coupling of data transfer between multiple software components is complicated and difficult to implement using traditional event-driven architectures.


Background
----------

Myosin was originally designed to address software problems when developing embedded control systems with command and control capabilities from multiple external entities. 

Since state data handled by myosin we incidentally have a solution for application fault-tolerance. Myosin comes equipped with the ability to cache system state objects into persistant storage when a system state model is updated. If the application crashes and restarts, myosin will load the previously cached system state back into the system and trigger the appropriate subscriber functions to recover the system before it

Philosophy
----------
The ``myosin`` engine is modelled off system environment variables. Environment variables are fully permissive and describe the context for a software runtimes. ``Myosin`` mimics an environment variable manager for strictly typed python objects called ``StateModels`` which describes a component of the software system. These ``StateModels`` 

Strictly Typed API
~~~~~~~~~~~~~~~~~~
Models loaded into ``myosin`` are strictly typed with property getters and setters on each field. All myosin functions are strictly typed for intellisense and static type analysis tools like Pylance.

Fully Permissive
~~~~~~~~~~~~~~~~
Any software component can access and subscribe to system state models agnostic of your projects hierarchical structure. Simply import ``myosin`` from anywhere and get access to the systems state.

Thread Safety
~~~~~~~~~~~~~
Access to state models are fully thread-safe and support concurrent read and write operations to the system state. Access to myosin state models are done using the checkout mechanic and state model writes are done using state commits

#. Lightweight: Small dependancy tree and low operating footprint

Core Features
~~~~~~~~~~~~~
#. Built-in application state recovery.
#. Support for singleton object storage.
#. Support for custom validation before state writes are
#. State-driven Asynchronous callback triggers

Design
======

In order to make the state manager thread  safe and guard against saving potentially invalid states I will divide the module-state interaction as a two layer process:
1. Runtime Layer - Holds the system runtime models as they represent the current state
2. Checkout Layer - Generates copies of runtime models to distribute externally for modification




Checkout
~~~~~~~~

An external module makes a request to the state manager to create a copy of a loaded runtime model. The state manager accesses the runtime layer and generates a copy of the requested model and forwards it to the external module. The module can make any changes it wants to that module copy and it will not affect the system state. This is desired because the state changes must be validated by the state manager before the state is modified (this includes sending state changes to the firmware to ensure they are accepted since these are independant systems). Remember if a bad state change is saved into the runtime layer, another async request has the potential to read a bad state.

Configuration
~~~~~~~~~~~~~

The checked-out copy of the runtime model can then be configured and potentially even malformed with no affect to the state. If something goes wrong during the checkout the copy will simply be dereferenced by the stack as a local variable. The runtime model will have a set of preconditions to validate all setter attributes.

State Commit
~~~~~~~~~~~~

Once the desired state changes have been made we can commit our modified copy to the system for state-level validation. The state manager will first apply our modified model to the firmware and try to see if the values are accepted. If the changes are accepted it will immediately update the runtime model and perform callbacks on all registered subscribers to that models state changes. Some models such as `Device` and `Experiment` models may not require any additional validation that extends the preconditions in which case commit will simply skip the firmware validation phase. Once all subscribers are updated with the change the cache is written with the new runtime model state.

