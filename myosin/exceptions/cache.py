# -*- coding: utf-8 -*-
"""
Model Caching Exceptions
========================
"""


class CacheException(Exception):
    """
    General model cache exception.
    """

    def __init__(self, msg: str = "Cache encountered a general exception") -> None:
        self.message = msg


class CachePathError(CacheException):
    """
    Raised on failure resolving caching path.
    """


class NullCachePathError(CacheException):
    """
    Raised on unset caching basepath. Basepath must be specified with the ``MYOSIN_CACHE_BASE_PATH``
    environment variable.
    """
