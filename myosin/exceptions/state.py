# -*- coding: utf-8 -*-
"""
State Exceptions
================

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""


class StateException(Exception):
    """
    General state context exception.
    """

    def __init__(self, msg: str = "State encountered a general exception") -> None:
        self.message = msg


class UninitializedStateError(StateException):
    """
    Raised if a registration request is made on a model with one or more uninitialized properties.
    Verify the model can be serialized before it is registered with 
    :func:`myosin.models.state.StateModel.serialize`
    """

    def __init__(self, msg: str = "") -> None:
        super().__init__(msg)


class ModelNotFound(StateException):
    """
    Raised if the requested state model is not found in the internal state registry. Usually this 
    means state actions are being requested on a model before it has been registered.
    """

    def __init__(self, msg: str = "The requested model is not found") -> None:
        super().__init__(msg=msg)
