# -*- coding: utf-8 -*-
"""
State Exceptions
=====================
Modified: 2021-11
"""


class StateException(Exception):
    def __init__(self, msg: str = "StateIO encountered a general exception") -> None:
        self.message = msg


class NullCheckoutError(StateException):
    def __init__(self, msg: str = "The requested model does not exist in state registry") -> None:
        super().__init__(msg=msg)
