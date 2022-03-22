# -*- coding: utf-8 -*-
"""
Myosin
======
Modified: 2022-03

Lightweight & threadsafe state engine
"""

import logging

from myosin.__version__ import __version__
from myosin.typing import _PKey
from myosin.models.base import BaseModel
from myosin.models.state import StateModel
from myosin.state import State

__all__ = [
    '__version__',
    'BaseModel',
    'StateModel',
    '_PKey',
    'State'
]

_log = logging.getLogger(__name__)
_log.info("Myosin version %s", __version__)
