# -*- coding: utf-8 -*-
"""
Myosin
======

Lightweight and thread-safe state management engine for developing state-driven systems. Import the 
global state context manager from anywhere to access registered state models ``from myosin import State``.

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

import logging
from myosin.state import State
from myosin.__version__ import __version__
from myosin.models.state import StateModel
from myosin.utils.metrics import Metrics as metrics

__all__ = [
    '__version__',
    '__author__',
    'StateModel',
    'State'
]
__author__ = "Christian Sargusingh <christian@leapsystems.online>"

_log = logging.getLogger(__name__)
_log.info("Myosin version %s", __version__)
# export version to prometheus
metrics.meta.info({'version': __version__})
