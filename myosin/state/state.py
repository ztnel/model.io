# -*- coding: utf-8 -*-
"""
Myosin State Engine
===================
Modified: 2022-04

"""
import asyncio
import copy
import logging
from typing import Dict, Type, TypeVar, Callable

from myosin.state.ssm import SSM
from myosin.typing import AsyncCallback
from myosin.utils.funcs import pformat
from myosin.models.state import StateModel
from myosin.utils.concurrency import ThreadUtils as tutils
from myosin.exceptions.state import HashNotFound, NullCheckoutError, UninitializedStateError

# generic runtime model type
_T = TypeVar('_T', bound=StateModel)


class State:

    # storage mechanism is { name: Model }
    _ssm: Dict[int, SSM] = {}

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): ...

    def load(self, model: _T) -> _T:
        """
        Load state model into memory

        :param model: state model
        :type model: StateModel
        """
        self._ssm[model.__typehash__()] = SSM[_T](model)
        # assert the model attributes are initialized
        try:
            model.serialize()
        except AttributeError as exc:
            raise UninitializedStateError from exc
        self._logger.info("Loaded state model: %s", pformat(model.serialize()))
        return model

    @tutils.lock(tutils.state_lock)
    def checkout(self, state_type: Type[_T]) -> _T:
        """
        Returns reference of requested state model

        :param state_type: requested state model reference 
        :type state_type: Type[_T]
        :raises NullCheckoutError: if the requested state type does not exist 
        :return: deep copy of requested state model
        :rtype: _T
        """
        self._logger.info("Checking out state model of type %s", state_type)
        _type_hash = hash(state_type)
        self._logger.debug("Computed type hash: %s", _type_hash)
        ssm = self._ssm.get(_type_hash)
        if not ssm:
            raise NullCheckoutError
        return copy.deepcopy(ssm.ref)

    @tutils.lock(tutils.state_lock)
    def commit(self, state: _T, cache: bool = False) -> _T:
        """
        Commit new state to system state and update state subscriber callbacks

        :param state: modified copy of state
        :type state: _T
        :param cache: cache the state to disk once updated, defaults to False
        :type cache: bool, optional
        :raises HashNotFound: if system state has no state registered of the requested type 
        :return: updated system state reference
        :rtype: _T
        """
        # automatic type inference by typehash
        _type_hash = hash(type(state))
        # verify typehash
        ssm = self._ssm.get(_type_hash)
        if not ssm:
            self._logger.error("Committed typehash: %s did not match any state model", _type_hash)
            raise HashNotFound
        ssm.ref = state
        asyncio.run(ssm.execute())
        if cache:
            state.cache()
            self._logger.debug("Cached commited state model %s", state)
        return state

    def subscribe(self, state_type: Type[_T], callback: Callable[[_T], AsyncCallback]) -> None:
        """
        Subscribe an asynchronous state change listener to a designated runtime model

        :param state_type: model type to subscribe to
        :type state_type: Type[T]
        :param callback: state change listener callback
        :type callback: Callable[[T], AsyncCallback]
        """
        _type_hash = hash(state_type)
        ssm = self._ssm.get(_type_hash)
        if not ssm:
            self._logger.error("Subscribed typehash: %s did not match any state model", _type_hash)
            raise HashNotFound
        ssm.queue.append(callback)

    def reset(self) -> None:
        """
        Reset all loaded state model
        """
        self._ssm.clear()
