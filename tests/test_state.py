# -*- coding: utf-8 -*-
"""
State Unittests
===============
Modified: 2022-04

"""

import copy
import asyncio
import logging
from typing import Dict
import unittest
from unittest.mock import MagicMock, patch

from myosin.models.state import StateModel
from myosin import State
from myosin.state.ssm import SSM
from myosin.exceptions.state import ModelNotFound, UninitializedStateError


class TestState(unittest.TestCase):

    def setUp(self) -> None:
        logging.disable()
        self.test_state = MagicMock(spec=StateModel)
        self.test_state.__typehash__ = MagicMock()
        self.test_state.__typehash__.return_value = hash(MagicMock)
        self.test_ssm = MagicMock(spec=SSM)
        self.test_ssm.ref = self.test_state
        self.state = State()

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        self.state._ssm.clear()
        del self.state

    @patch("myosin.state.state.pformat", lambda x: None)
    def test_uninitialized_load(self):
        """
        Test loading an uninitalized model
        """
        self.test_state.serialize.side_effect = AttributeError
        with self.assertRaises(UninitializedStateError):
            self.state.load(self.test_state)
        self.test_state.load.assert_called_once()

    def test_cm_lock(self):
        """
        Test context manager lock aquisition and release
        """
        def mock_iter(_):
            for x in [a1, a2]:
                yield x
        a1, a2 = MagicMock(spec=SSM), MagicMock(spec=SSM)
        self.state._logger = MagicMock()
        mock_accessors = MagicMock()
        self.state.accessors = mock_accessors
        mock_accessors.__iter__ = mock_iter
        # build mock accessors array and validate acquire and release are called iteratively
        with self.state:
            a1.lock.acquire.assert_called_once()
            a2.lock.acquire.assert_called_once()
        a1.lock.release.assert_called_once()
        a2.lock.release.assert_called_once()

    @patch.object(SSM, "__init__", lambda x, y: None)
    @patch("myosin.state.state.pformat", lambda x: None)
    def test_load(self):
        """
        Test state load keyset and SSM wrapper configuration
        """
        # initialize model
        self.test_state.name = "test"
        res_state = self.state.load(self.test_state)
        self.test_state.load.assert_called_once()
        self.test_state.serialize.assert_called_once()
        # im setting the test like this in order to test both the keyset and the object set,
        # I want to raise test assertion failures rather than key errors.
        ssm = self.state._ssm.get(self.test_state.__typehash__())
        self.assertIsNotNone(ssm)
        self.assertEqual(res_state, self.test_state)

    def test_null_checkout(self):
        """
        Test null checkout fails with ModelNotFound
        """
        with self.assertRaises(ModelNotFound):
            _ = self.state.checkout(MagicMock)

    @patch.object(copy, "deepcopy")
    def test_checkout(self, mock_deepcopy: MagicMock):
        """
        Test checkout copy
        """
        dcm = MagicMock()
        mock_deepcopy.return_value = dcm
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        dc_state = self.state.checkout(MagicMock)
        self.assertEqual(dc_state, dcm)

    @patch.object(copy, "deepcopy")
    def test_unregistered_commit(self, mock_deepcopy: MagicMock):
        """
        Test unregistered state commit
        """
        mock_deepcopy.return_value = self.test_state
        with self.assertRaises(ModelNotFound):
            self.state.commit(self.test_state)

    @patch.object(copy, "deepcopy")
    def test_cached_commit(self, mock_deepcopy: MagicMock):
        """
        Test state commit with caching
        """
        mock_deepcopy.return_value = self.test_state
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        self.state.commit(self.test_state, cache=True)
        self.test_state.cache.assert_called_once()

    @patch.object(copy, "deepcopy")
    def test_commit(self, mock_deepcopy: MagicMock):
        """
        Test state commit object assignment logic
        """
        mock_deepcopy.return_value = self.test_state
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        self.state.commit(self.test_state)

    @unittest.skip("Refactoring async implementation")
    @patch.object(copy, "deepcopy")
    @patch.object(asyncio, 'run')
    def test_commit_with_async_queue(self, mock_run: MagicMock, mock_deepcopy: MagicMock):
        """
        Test state commit with async callback queue
        """
        mock_deepcopy.return_value = self.test_state
        self.test_ssm.queue = [1]
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        self.state.commit(self.test_state)
        self.test_ssm.execute.assert_called_once()
        mock_run.assert_called_once()

    def test_clear(self):
        """
        Test state model clear
        """
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        self.state.reset()
        self.test_ssm.ref.clear.assert_called_once()

    def test_subscription_hash_not_found(self):
        """
        Test subscription on unregistered state model
        """
        async def callback(demo: MagicMock) -> None: ...
        mock_ssm = self.mock_ssm(self.state._ssm)
        mock_ssm.get.return_value = None
        with self.assertRaises(ModelNotFound):
            self.state.subscribe(MagicMock, callback)

    def test_subscription(self):
        """
        Test subscription (sanity)
        """
        async def callback(_: MagicMock) -> None: ...
        self.state._ssm[self.test_state.__typehash__()] = self.test_ssm
        self.state.subscribe(MagicMock, callback)
        self.test_ssm.queue.append.assert_called_once_with(callback)

    @staticmethod
    def mock_ssm(ssm: Dict) -> MagicMock:
        mm = MagicMock()
        mm.__getitem__.side_effect = ssm.__getitem__
        return mm
