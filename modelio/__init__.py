# -*- coding: utf-8 -*-

__all__ = ['__version__']

import logging
from modelio.__version__ import __version__

_log = logging.getLogger(__name__)
_log.info("Model.io version %s", __version__)
