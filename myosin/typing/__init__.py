# -*- coding: utf-8 -*-
from typing import Any, Coroutine, Union


__all__ = [
    "PrimaryKey"
]

PrimaryKey = Union[int, str]
AsyncCallback = Coroutine[Any, Any, None]
