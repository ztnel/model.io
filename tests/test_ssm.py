# -*- coding: utf-8 -*-
"""
SSM Unittests
=============
Modified: 2022-04
"""

import asyncio
from asyncio.events import AbstractEventLoop
import unittest
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from threading import Lock
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

    async def test_cb_runner(self):
        """
        Test execution runner and exception reporting
        """
        alpha_cb = AsyncMock()
        alpha_cb.side_effect = BaseException
        beta_cb = AsyncMock()
        self.ssm.queue = [alpha_cb, beta_cb]
        await self.ssm.cb_runner()
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

    def test_lock(self):
        """
        Test threading lock property get/set
        """
        mock_lock = MagicMock(spec=Lock)
        self.ssm.lock = mock_lock
        self.assertEqual(self.ssm.lock, mock_lock)

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

    @patch.object(SSM, "cb_runner")
    @patch.object(SSM, "_get_asyncio_ctx")
    def test_execute(self, _get_asyncio_ctx: MagicMock, cb_runner: AsyncMock):
        """
        Test async execution wrapper
        """
        mock_loop = MagicMock(spec=AbstractEventLoop)
        _get_asyncio_ctx.return_value = mock_loop
        # test running loop ctx
        mock_loop.is_running.return_value = True
        self.ssm.execute()
        mock_loop.create_task.assert_called_once()
        mock_loop.run_until_complete.assert_not_called()
        mock_loop.reset_mock()
        # test running loop ctx
        mock_loop.is_running.return_value = False
        self.ssm.execute()
        mock_loop.create_task.assert_not_called()
        self.assertEqual(mock_loop.run_until_complete.call_count, 2)
        mock_loop.close.assert_called_once()

    @patch.object(asyncio, "new_event_loop")
    @patch.object(asyncio, "get_running_loop")
    def test_get_asyncio_ctx(self, get_running_loop: MagicMock, new_event_loop: MagicMock) -> None:
        """
        Test asyncio context is able to be fetched
        """
        mock_loop = MagicMock()
        get_running_loop.return_value = mock_loop
        self.assertEqual(self.ssm._get_asyncio_ctx(), mock_loop)
        new_event_loop.return_value = mock_loop
        get_running_loop.side_effect = RuntimeError
        self.assertEqual(self.ssm._get_asyncio_ctx(), mock_loop)
        new_event_loop.assert_called_once()
