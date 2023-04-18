# -*- coding: utf-8 -*-
"""
Myosin
======

Lightweight and thread-safe state management engine for developing state-driven systems. Import the 
global state context manager from anywhere to access registered state models ``from myosin import State``.

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

import logging
from myosin.__version__ import __version__

__all__ = [
    '__version__',
    '__author__',
]
__author__ = "Christian Sargusingh <christian@leapsystems.online>"
_log = logging.getLogger(__name__)
_log.info("Myosin version %s", __version__)
