# -*- coding: utf-8 -*-
"""
Concurrency Utils Unittests
===========================
Modified: 2022-03
"""

import unittest
import logging

from myosin.utils.concurrency import ThreadUtils as tutils


class TestConcurrency(unittest.TestCase):

    def setUp(self) -> None:
        logging.disable()

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)

    def test_lock(self):
        """
        Test lock decorator
        """
        @tutils.lock(tutils.state_lock)
        def test_method() -> bool:
            self.assertTrue(tutils.state_lock.locked())
            return True
        self.assertFalse(tutils.state_lock.locked())
        self.assertTrue(test_method())
