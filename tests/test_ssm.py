# -*- coding: utf-8 -*-
"""
SSM Unittests
=============
Modified: 2022-04
"""

import unittest
import logging
from unittest.mock import AsyncMock, patch
from myosin.state.ssm import SSM
from tests.resources.models import DemoState


class TestAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        logging.disable()
        self.test_state = DemoState(1)
        self.ssm = SSM[DemoState](self.test_state)

    def tearDown(self) -> None:
        del self.ssm
        logging.disable(logging.NOTSET)

    async def test_execute(self):
        """
        Test execution runner and exception reporting
        """
        alpha_cb = AsyncMock()
        alpha_cb.side_effect = BaseException
        beta_cb = AsyncMock()
        self.ssm.queue = [alpha_cb, beta_cb]
        await self.ssm.execute()
        alpha_cb.assert_called_once()
        beta_cb.assert_called_once()


class TestSSM(unittest.TestCase):

    def setUp(self) -> None:
        logging.disable()
        self.test_state = DemoState(1)
        self.ssm = SSM[DemoState](self.test_state)

    def tearDown(self) -> None:
        del self.ssm
        logging.disable(logging.NOTSET)

    def test_ref_autoset(self):
        """
        Test reference is autoset in ssm init
        """
        self.assertEqual(self.ssm.ref, self.test_state)

    def test_reference_hash(self):
        """
        Test for correct reference hash return
        """
        self.assertEqual(self.ssm.refhash, hash(self.test_state))

    def test_type_hash(self):
        """
        Test for correct type hash return
        """
        self.assertEqual(self.ssm.typehash, self.test_state.__typehash__())

    def test_ref(self):
        """
        Test reference object get/set
        """
        new_state = DemoState(2)
        self.ssm.ref = new_state
        self.assertEqual(self.ssm.ref, new_state)

    def test_queue(self):
        """
        Test async queue callback get/set
        """
        async def async_callback(_: DemoState): ...
        new_queue = [async_callback]
        self.ssm.queue = new_queue
        self.assertEqual(self.ssm.queue, new_queue)
