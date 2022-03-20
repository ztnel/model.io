# -*- coding: utf-8 -*-
"""
Model IO
========
Modified: 2022-03

Lightweight & threadsafe state engine
"""

import logging
from modelio.__version__ import __version__
from modelio.typing import _PKey
from modelio.models.base import BaseModel
from modelio.models.state import StateModel
from modelio.state import State

__all__ = [
    '__version__',
    'BaseModel',
    'StateModel',
    '_PKey',
    'State'
]

_log = logging.getLogger(__name__)
_log.info("Model.io version %s", __version__)
