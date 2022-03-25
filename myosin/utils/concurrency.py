# -*- coding: utf-8 -*-
"""
Concurrency Utils
=================
Modified: 2022-03
"""

import logging
from threading import Lock
from typing import Callable, TypeVar

_T = TypeVar('_T')


class ThreadUtils:

    _logger = logging.getLogger(__name__)
    state_lock = Lock()

    @classmethod
    def lock(cls, lock: Lock) -> Callable:
        """
        Apply a semaphore lock to decorated function

        :param lock: lock for resource
        :type lock: Lock
        :return: decorator
        :rtype: Callable
        """
        def decorator(func: Callable[..., _T]) -> Callable[..., _T]:
            def wrapper(*args, **kwargs) -> _T:
                with lock:
                    response = func(*args, **kwargs)
                return response
            return wrapper
        return decorator
