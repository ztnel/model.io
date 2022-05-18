# -*- coding: utf-8 -*-
"""
State Unittests
===============
Modified: 2022-04

"""

import asyncio
from typing import Dict
import unittest
import logging
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from myosin.models.state import StateModel
from tests.resources.models import DemoState

from myosin import State
from myosin.state.ssm import SSM
from myosin.exceptions.state import HashNotFound, NullCheckoutError, UninitializedStateError


class TestState(unittest.TestCase):

    def setUp(self) -> None:
        logging.disable()
        self.test_state = DemoState(1)
        self.state = State()

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        self.state._ssm.clear()
        del self.state

    def mock_loader(self):
        """
        State loading helper to remove interdependancy of testing methods
        """
        self.state._ssm[self.test_state.__typehash__()] = SSM[DemoState](self.test_state)

    @patch.object(StateModel, 'load')
    @patch.object(StateModel, 'serialize', side_effect=AttributeError)
    def test_uninitialized_load(self, _: MagicMock, load: MagicMock):
        """
        Test loading an uninitalized model
        """
        with self.assertRaises(UninitializedStateError):
            self.state.load(self.test_state)
        load.assert_called_once()

    def test_cm_lock(self):
        """
        Test context manager state lock aquisition and release
        """
        # NOTE: threading.Lock methods cannot be mocked
        with State() as state:
            self.assertTrue(state.state_lock.locked())
        self.assertFalse(state.state_lock.locked())

    @patch.object(StateModel, 'load')
    @patch.object(DemoState, 'serialize', **{'return_value': "test"})
    def test_load(self, serialize: MagicMock, load: MagicMock):
        """
        Test state load keyset and SSM wrapper configuration
        """
        # initialize model
        self.test_state.name = "test"
        self.state.load(self.test_state)
        load.assert_called_once()
        serialize.assert_called_once()
        # im setting the test like this in order to test both the keyset and the object set,
        # I want to raise test assertion failures rather than key errors.
        ssm = self.state._ssm.get(self.test_state.__typehash__())
        self.assertIsNotNone(ssm)
        if ssm is not None:
            self.assertEqual(ssm.ref, self.test_state)

    def test_null_checkout(self):
        """
        Test null checkout fails with NullCheckoutError
        """
        with self.assertRaises(NullCheckoutError):
            _ = self.state.checkout(DemoState)

    def test_checkout(self):
        """
        Test checkout copy
        """
        self.mock_loader()
        test_state = self.state.checkout(DemoState)
        self.assertNotEqual(hash(test_state), hash(self.test_state))

    def test_unregistered_commit(self):
        """
        Test unregistered state commit
        """
        with self.assertRaises(HashNotFound):
            self.state.commit(self.test_state)

    @patch.object(SSM, 'execute', new_callable=AsyncMock)
    @patch.object(StateModel, 'cache')
    def test_cached_commit(self, cache: MagicMock, execute: AsyncMock):
        """
        Test state commit with caching
        """
        self.mock_loader()
        self.state.commit(self.test_state, cache=True)
        execute.assert_awaited_once()
        cache.assert_called_once()

    @patch.object(SSM, 'execute', new_callable=AsyncMock)
    @patch.object(StateModel, 'cache')
    def test_uncached_commit(self, cache: MagicMock, execute: AsyncMock):
        """
        Test state commit without caching
        """
        self.mock_loader()
        self.state.commit(self.test_state)
        execute.assert_awaited_once()
        cache.assert_not_called()

    @patch.object(asyncio, 'run')
    def test_commit_hash_not_found(self, run: MagicMock):
        """
        Test commit on unregistered state model
        """
        mock_ssm = self.mock_ssm(self.state._ssm)
        mock_ssm.get.return_value = None
        with self.assertRaises(HashNotFound):
            self.state.commit(self.test_state)
        run.assert_not_called()

    @patch.object(StateModel, 'clear')
    def test_clear(self, clear: MagicMock):
        """
        Test state model clear
        """
        self.mock_loader()
        self.state.reset()
        clear.assert_called_once()

    def test_subscription_hash_not_found(self):
        """
        Test subscription on unregistered state model
        """
        async def callback(demo: DemoState) -> None: ...
        mock_ssm = self.mock_ssm(self.state._ssm)
        mock_ssm.get.return_value = None
        with self.assertRaises(HashNotFound):
            self.state.subscribe(DemoState, callback)

    @patch.object(SSM, 'queue', new_callable=PropertyMock)
    def test_subscription(self, queue: MagicMock):
        """
        Test subscription on unregistered state model
        """
        async def callback(demo: DemoState) -> None: ...
        self.mock_loader()
        self.state.subscribe(DemoState, callback)
        queue.return_value.append.assert_called_once_with(callback)

    @staticmethod
    def mock_ssm(ssm: Dict) -> MagicMock:
        mm = MagicMock()
        mm.__getitem__.side_effect = ssm.__getitem__
        return mm
