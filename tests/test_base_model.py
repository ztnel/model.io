# -*- coding: utf-8 -*-
"""
Base Model Unittests
====================
Modified: 2022-03
"""

import unittest
import logging
from unittest.mock import patch

from myosin.models.base import BaseModel


class TestBaseModel(unittest.TestCase):

    @patch.multiple(BaseModel, __abstractmethods__=set())
    def setUp(self) -> None:
        logging.disable()
        self.base = BaseModel(1)  # type: ignore

    def tearDown(self) -> None:
        del self.base
        logging.disable(logging.NOTSET)

    def test_typehash(self):
        self.base.__typehash__()

    @patch.multiple(BaseModel, __abstractmethods__=set())
    def test_eq(self):
        self.comparator = BaseModel(2)  # type: ignore

    def test_id(self):
        """
        Test base model id get/set
        """
        self.assertEqual(self.base.id, 1)
        self.base.id = 2
        self.assertEqual(self.base.id, 2)
