# -*- coding: utf-8 -*-
"""
State Unittests
===============
Modified: 2022-04

"""

import unittest
import logging
from unittest.mock import patch
from tests.resources.models import DemoState

from myosin import State
from myosin.state.ssm import SSM
from myosin.exceptions.state import HashNotFound, NullCheckoutError, UninitializedStateError


class TestState(unittest.TestCase):

    def setUp(self) -> None:
        logging.disable()
        self.test_state = DemoState(1)
        with State() as state:
            self.state = state

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        self.state.reset()

    def mock_loader(self):
        """
        State loading helper to remove interdependancy of testing methods
        """
        self.state._ssm[self.test_state.__typehash__()] = SSM[DemoState](self.test_state)

    def test_uninitialized_load(self):
        """
        Test loading an uninitalized model
        """
        with self.assertRaises(UninitializedStateError):
            self.state.load(self.test_state)

    def test_load(self):
        """
        Test state load keyset and SSM wrapper configuration
        """
        # initialize model
        self.test_state.name = "test"
        self.state.load(self.test_state)
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

    @patch('asyncio.run', lambda x: None)
    def test_commit(self):
        """
        Test state commit
        """
        self.mock_loader()
        self.state.commit(self.test_state)
