=====
About
=====

Myosin is a lightweight framework for developing state-driven software applications. 

are useful for allowing multiple software components within an application to communicate using the same base syntax. The syntax for communication of data is implemented through the state models which represent the the states of different components of the software.

Myosin was originally designed for a complex multiple-input multiple-output embedded system which provided command and control synchronization between an embedded device, real-time cloud service and an internal REST API. Every component operated in unison. Any change made on the device locally required a synchronous cloud update event and vice-versa. Tight coupling of data transfer between multiple software components is complicated and difficult to implement using traditional event-driven architectures.

Core Features
=============
#. Support for singleton runtime objects to descibe system states.
#. State-driven callback triggers
#. Provide a validation layer before state changes
#. against preconditions (internally in the models)
#. Facilitate automated system caching on state changes (Facilitate system state recovery from cached models)
#. Fully permissive -> any module can access and subscribe to state change events
#. Clean and easy to use API.
#. thread-safe
#. Lightweight -> only built-in python libraries


Design Philosophy
-----------------

In order to make the state manager thread  safe and guard against saving potentially invalid states I will divide the module-state interaction as a two layer process:
1. Runtime Layer - Holds the system runtime models as they represent the current state
2. Checkout Layer - Generates copies of runtime models to distribute externally for modification

Checkout
~~~~~~~~

An external module makes a request to the state manager to *checkout* a current runtime model. The state manager accesses the runtime layer and generates a copy of the requested model and forwards it to the external module. The module can make any changes it wants to that module copy and it will not affect the system state. This is desired because the state changes must be validated by the state manager before the state is modified (this includes sending state changes to the firmware to ensure they are accepted since these are independant systems). Remember if a bad state change is saved into the runtime layer, another async request has the potential to read a bad state.

Configuration
~~~~~~~~~~~~~

The checked-out copy of the runtime model can then be configured and potentially even malformed with no affect to the state. If something goes wrong during the checkout the copy will simply be dereferenced by the stack as a local variable. The runtime model will have a set of preconditions to validate all setter attributes.

State Commit
~~~~~~~~~~~~

Once the desired state changes have been made we can commit our modified copy to the system for state-level validation. The state manager will first apply our modified model to the firmware and try to see if the values are accepted. If the changes are accepted it will immediately update the runtime model and perform callbacks on all registered subscribers to that models state changes. Some models such as `Device` and `Experiment` models may not require any additional validation that extends the preconditions in which case commit will simply skip the firmware validation phase. Once all subscribers are updated with the change the cache is written with the new runtime model state.

