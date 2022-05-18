Usage
=====

System Requirements
-------------------

*Myosin* is built for use on embedded linux platforms. Some features of *myosin* are only written for POSIX compliant systems. Cross-platform support for all features is not currently being pursued.

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~
The table below outlines the distributions and test suite support of *myosin* against different python versions: 

====== =========== =============
Python Distibution Test Suite
====== =========== =============
3.8    Supported   Supported
------ ----------- -------------
3.9    Supported   Supported
------ ----------- -------------
3.10   Supported   Not Supported
====== =========== =============


Installation
------------

The easiest way to install ``myosin`` is using ``pip``:

.. code-block:: console

   python3 -m pip install myosin

Alternatively you can build from source:

.. code-block:: console

   git clone git@github.com:ztnel/myosin.git
   cd myosin
   python3 -m pip install .


Basic Usage
-----------
Start by defining a model by creating a class that implements ``StateModel``:

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

Advanced Usage
--------------
Coming soon.

Developer Tips
--------------
Coming soon.

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

.. warning::
   The ``nosetests`` utility is no longer maintained and has compatibility issues with Python 3.10 as noted by this `issue thread <https://github.com/nose-devs/nose/issues/1099>`_. Therefore *myosin* unittests will not be executable on Python 3.10.

   I am looking to migrate to pytest and would love contributor support in unittesting.

The test runner will report the executed tests and generate a coverage report. The coverage goal for this library is 95% or greater. If you want to contribute and don't know how, this is a great place to start.
