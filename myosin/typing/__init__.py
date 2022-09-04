# -*- coding: utf-8 -*-
"""
Typing
======

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

from typing import Any, Coroutine, Union


__all__ = [
    "PrimaryKey",
    "AsyncCallback"
]

#: :class:`myosin.models.state.StateModel` id type alias
PrimaryKey = Union[int, str]
#: Asynchronous method type
AsyncCallback = Coroutine[Any, Any, None]
