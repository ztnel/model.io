# -*- coding: utf-8 -*-
from typing import Any, Coroutine, Union


__all__ = [
    "_PKey"
]

_PKey = Union[int, str]
AsyncCallback = Coroutine[Any, Any, None]
