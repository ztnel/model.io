# -*- coding: utf-8 -*-

__all__ = ['__version__', 'BaseModel', 'StateModel', '_PKey']

import logging
from modelio.__version__ import __version__
from modelio.typing import _PKey
from modelio.models.base import BaseModel
from modelio.models.state import StateModel

_log = logging.getLogger(__name__)
_log.info("Model.io version %s", __version__)
