# -*- coding: utf-8 -*-
"""
Base Model Unittests
====================
Modified: 2022-03
"""

import unittest
import logging
from unittest.mock import patch, MagicMock

from myosin.models.base import BaseModel


class TestBaseModel(unittest.TestCase):

    @patch.multiple(
        BaseModel,
        __abstractmethods__=set(),
        serialize=MagicMock(),
        deserialize=MagicMock()
    )
    def setUp(self) -> None:
        logging.disable()
        self.base = BaseModel(1)  # type: ignore
        self.comparator = BaseModel(2)  # type: ignore

    def tearDown(self) -> None:
        del self.base
        logging.disable(logging.NOTSET)

    def test_hash(self):
        """
        Test hashing
        """
        self.assertNotEqual(self.base.__hash__(), self.comparator.__hash__())

    def test_typehash(self):
        """
        Test type hashing
        """
        self.assertEqual(self.base.__typehash__(), self.comparator.__typehash__())

    def test_repr(self):
        """
        Test base model repr
        """
        self.assertEqual(type(self.base.__repr__()), str)

    def test_eq(self):
        """
        Test base model equality comparator
        """
        # test base model comparisons with different ids
        self.assertFalse(self.base == self.comparator)
        # test base model comparison with same id
        self.comparator.id = 1
        self.assertTrue(self.base == self.comparator)
        # test non model comparison
        self.assertFalse(self.base == object())

    def test_id(self):
        """
        Test base model id get/set
        """
        self.base.id = 2
        self.assertEqual(self.base.id, 2)
