# -*- coding: utf-8 -*-
"""
State Exceptions
=====================
Modified: 2021-11
"""


class CacheException(Exception):
    def __init__(self, msg: str = "Cache encountered a general exception") -> None:
        self.message = msg


class CachePathError(CacheException):
    pass


class NullCachePathError(CacheException):
    pass
