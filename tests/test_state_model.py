# -*- coding: utf-8 -*-
"""
State Model Unittests
=====================
Modified: 2022-03
"""

import os
import json
import builtins
import unittest
import logging
from unittest.mock import MagicMock, patch, mock_open
from tests.resources.errors import JSON_DECODE_ERROR
from tests.resources.models import SERIALIZED_MODEL

from myosin.models.state import StateModel
from myosin.exceptions.cache import CachePathError, NullCachePathError


class TestStateModel(unittest.TestCase):

    @patch.multiple(
        StateModel,
        __abstractmethods__=set(),
        serialize=lambda x, y: SERIALIZED_MODEL,
        deserialize=lambda x, **y: None
    )
    def setUp(self) -> None:
        logging.disable()
        self.state = StateModel(1)  # type: ignore

    def tearDown(self) -> None:
        del self.state
        logging.disable(logging.NOTSET)

    def test_null_cache_path(self):
        """
        Test null cache path exception raise
        """
        with self.assertRaises(NullCachePathError):
            self.state.cache()

    def test_cache_path_existance(self):
        """
        Test cache path existance check
        """
        # inject a bad cache path
        self.state.cache_base_path = '\\'
        with self.assertRaises(CachePathError):
            self.state.cache()

    @patch.object(json, 'dump')
    @patch('builtins.open', mock_open())
    @patch.object(StateModel, 'serialize')
    def test_cache(self, dump: MagicMock, serialize: MagicMock):
        """
        Test caching mechanism
        """
        self.state.cache_base_path = '.'
        self.state.cache()
        dump.assert_called_once()
        serialize.assert_called_once()

    @patch.object(json, 'load')
    @patch('builtins.open', mock_open())
    def test_load_decode_error(self, load: MagicMock):
        """
        Test load decode error is handled gracefully
        """
        load.side_effect = JSON_DECODE_ERROR
        self.state.load()

    @patch.object(builtins, 'open')
    def test_load_fnf(self, open: MagicMock):
        """
        Test load file not found error is handled gracefully 
        """
        open.side_effect = FileNotFoundError
        self.state.load()

    @patch.object(json, 'load')
    @patch('builtins.open', mock_open())
    @patch.object(StateModel, 'deserialize')
    def test_load(self, deserialize: MagicMock, load: MagicMock):
        """
        Test loading mechanism
        """
        self.state.load()
        load.assert_called_once()
        deserialize.assert_called_once()

    @patch.object(os.path, 'exists')
    @patch.object(os, 'remove')
    def test_clear(self, remove: MagicMock, exists: MagicMock):
        """
        Test cache clearing mechanism
        """
        exists.return_value = True
        self.state.clear()
        remove.assert_called_once_with(self.state._cpath)
        remove.reset_mock()
        exists.return_value = False
        self.state.clear()
        remove.assert_not_called()
