Usage
=====

Requirements
------------

Some features of ``myosin`` are only supported on POSIX compliant systems. Cross-platform support for all features is not being pursued. ``Myosin`` is only tested against Python ``3.7``, ``3.8`` and ``3.9``. Support for other versions will be supported in the future.

Installation
------------

To use ``myosin`` install it using pip:

.. code-block:: console

   python3 -m pip install myosin

Alternatively you can build from source:

.. code-block:: console

   git clone git@github.com:ztnel/myosin.git
   cd myosin
   python3 -m pip install .


Basic Usage
-----------
Start by defining a model by creating a class that implements `StateModel`:

.. code-block:: python


   from myosin import StateModel

   class User(StateModel):

      def __init__(self, name: str, email: str) -> None:
         super().__init__()
         self.name = name
         self.email = email

      @property
      def name(self) -> str:
         return self.__name

      @name.setter
      def name(self, name: str) -> None:
         self.__name = name

      @property
      def email(self) -> str:
         return self.__email

      @email.setter
      def email(self, email: str) -> None:
         self.__email = email

      def serialize(self) -> Dict[str, Any]:
         return {
            'id': self.id,
            'name': self.name,
            'email': self.email
         }

      def deserialize(self, **kwargs) -> None:
         for k, v in kwargs.items():
            setattr(self, k, v)

In the application entry load the default state model into the engine:

.. code-block:: python

   # create default state
   usr = User(
      name="chris",
      email="chris@email.com"
   )

   # register the model into the state engine
   with State() as state:
      state.load(usr)


In a consumer module you can access the global ``User`` model by checking out a copy of the model:

.. code-block:: python

   with State() as state:
      # checkout a copy of the user state model
      user = state.checkout(User)
   # read properties from the user state model
   logging.info("Username: %s", user.name)


In a producer module you can commit to the global ``User`` model by first checking out a copy of the model, modifying it and requesting a commit:

.. code-block:: python

   with State() as state:
      # checkout a copy of the user state model
      user = state.checkout(User)
      # modify user state model copy
      user.name = "cS"
      # commit the modified copy
      state.commit(user)

Testing
-------

Unittests can be executed locally by cloning ``myosin`` and installing the testing requirements:

.. code-block:: console

   git clone git@github.com:ztnel/myosin.git
   cd myosin
   python3 -m pip install tests/requirements.txt

Run the tests using the ``nosetests`` utility:

.. code-block:: console

   nosetests

The test runner will report the executed tests and generate a coverage report. The coverage goal for this library is 95% or greater. If you want to contribute and don't know how, this is a great place to start.


Checkout
~~~~~~~~

An external module makes a request to the state manager to create a copy of a loaded runtime model. The state manager accesses the runtime layer and generates a copy of the requested model and forwards it to the external module. The module can make any changes it wants to that module copy and it will not affect the system state. This is desired because the state changes must be validated by the state manager before the state is modified (this includes sending state changes to the firmware to ensure they are accepted since these are independant systems). Remember if a bad state change is saved into the runtime layer, another async request has the potential to read a bad state.

Configuration
~~~~~~~~~~~~~

The checked-out copy of the runtime model can then be configured and potentially even malformed with no affect to the state. If something goes wrong during the checkout the copy will simply be dereferenced by the stack as a local variable. The runtime model will have a set of preconditions to validate all setter attributes.

State Commit
~~~~~~~~~~~~

Once the desired state changes have been made we can commit our modified copy to the system for state-level validation. The state manager will first apply our modified model to the firmware and try to see if the values are accepted. If the changes are accepted it will immediately update the runtime model and perform callbacks on all registered subscribers to that models state changes. Some models such as `Device` and `Experiment` models may not require any additional validation that extends the preconditions in which case commit will simply skip the firmware validation phase. Once all subscribers are updated with the change the cache is written with the new runtime model state.

