Myosin
======
.. image:: https://badge.fury.io/py/myosin.svg
    :target: https://pypi.org/project/myosin/
    :alt: PyPi Project

.. image:: https://github.com/ztnel/myosin/actions/workflows/ci.yaml/badge.svg
    :target: https://github.com/ztnel/myosin/actions/workflows/ci.yaml
    :alt: Continuous Integration Status

.. image:: https://codecov.io/gh/ztnel/myosin/branch/master/graph/badge.svg?token=G2DNQAGVIP
    :target: https://codecov.io/gh/ztnel/myosin
    :alt: Code Coverage Summary

.. image:: https://readthedocs.org/projects/myosin/badge/?version=latest
    :target: https://myosin.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Modified: 2022-03

Lightweight state management engine.

About
-----
State-driven software architectures are useful for allowing multiple modules to be able to communicate using the same base syntax. The syntax for communication of data is implemented through the state models which represent the the states of different components of the software.

Quickstart
----------
Install `myosin` from pip

.. code-block:: bash

    python3 -m pip install myosin

Start by defining a model by creating a class that implements `StateModel` 

.. code-block:: python

    from myosin import _PKey
    from myosin import StateModel

    class User(StateModel):

        def __init__(self, _id: _PKey, name: str, email: str) -> None:
            super().__init__(_id)
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

In the application init load the default state model into the engine:

.. code-block:: python

    from myosin import _PKey

    usr = User(
        _id=1,
        name="chris",
        email="chris@email.com"
    )

    with State() as state:
        # register the model into the state engine
        state.load(usr)


In a consumer module you can access the global ``User`` model through a checked out copy:

.. code-block:: python

    with State() as state:
        # checkout a copy of the user state model
        user = state.checkout(User)
    # read properties from the user state model
    logging.info("Username: %s", user.name)


In a producer module you can commit to the global ``User`` model:

.. code-block:: python

    with State() as state:
        # checkout a copy of the user state model
        user = state.checkout(User)
        # modify user state model copy
        user.name = "cS"
        # commit the modified copy
        state.commit(user)


Contributions
-------------
Contributions are welcome! Please see the `issue backlog <https://github.com/ztnel/myosin/issues>`_ and `project kanban <https://github.com/ztnel/myosin/projects/1>`_ for active work items or contact me at `christian@leapsystems.online <mailto:christian@leapsystems.online>`_.

License
-------
This project is licensed under the terms of the `MIT License <LICENSE>`_
