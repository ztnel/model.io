# -*- coding: utf-8 -*-
"""
Typing
======

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

from typing import Any, Coroutine, Union


__all__ = [
    "PrimaryKey"
]

#: Hellow
PrimaryKey = Union[int, str]
#: Hellow
AsyncCallback = Coroutine[Any, Any, None]
