=====
About
=====

Myosin is a lightweight framework for developing state-driven software systems. The name describes a biological motor protein which converts chemical energy into mechanical energy making it the smallest engine known to man. 

Why Myosin?
-----------

State-driven systems are useful for allowing multiple software components within an application to communicate using the same language. The syntax for communication of data is implemented through the state models which are software representations. State-driven software is distinct from Finite-State Machine design patterns because state-driven systems are not required to follow a state machine map. 

.. image:: ../_static/event.png
    :align: center

Hellow

.. image:: ../_static/state.png
    :align: center

Background
----------

Myosin was originally designed to address software problems when developing embedded control systems with command and control capabilities from multiple external entities. Traditionally, embedded systems use an event-driven architecture for synchronizing state changes across multiple software components. The issue with events is that they are contextless. The subscriber must interpret the data and apply an update to its Systems where multiple entities can update a state variable and provide a synchronous real-time update to multiple other services. real-time cloud service and a REST API. Every endpoint made on the device locally required a synchronous cloud update event and vice-versa. Tight coupling of data transfer between multiple software components is complicated and difficult to implement using traditional event-driven architectures.

Since state data handled by myosin we incidentally have a solution for application fault-tolerance. Myosin comes equipped with the ability to cache system state objects into persistant storage when a system state model is updated. If the application crashes and restarts, myosin will load the previously cached system state back into the system and trigger the appropriate subscriber functions to recover the system before it

Philosophy
==========
The ``myosin`` engine is modelled off system environment variables. Environment variables are fully permissive and describe the context for a software runtimes. ``Myosin`` mimics an environment variable manager for strictly typed python objects called ``StateModels`` which describes a component of the software system. These ``StateModels`` 

Strictly Typed API
~~~~~~~~~~~~~~~~~~
Models loaded into ``myosin`` are strictly typed with property getters and setters on each field.

Fully Permissive
~~~~~~~~~~~~~~~~
Any software component can access and subscribe to system state models agnostic of your projects hierarchical structure. Simply import ``myosin`` from anywhere and get access to the systems state.

#. thread-safe
#. Lightweight: Small dependancy tree and low operating footprint

Core Features
~~~~~~~~~~~~~
#. Built-in application state recovery.
#. Support for singleton object storage.
#. Provide a validation layer before state changes against preconditions (internally in the models)
#. State-driven callback triggers

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

