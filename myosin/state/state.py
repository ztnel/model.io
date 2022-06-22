# -*- coding: utf-8 -*-
"""
Myosin State Engine
===================
Modified: 2022-04

"""
import copy
import asyncio
import logging
from threading import Lock
from typing import Dict, Type, TypeVar, Callable

from myosin.state.ssm import SSM
from myosin.typing import AsyncCallback
from myosin.utils.funcs import pformat
from myosin.models.state import StateModel
from myosin.exceptions.state import HashNotFound, NullCheckoutError, UninitializedStateError

# generic runtime model type
_T = TypeVar('_T', bound=StateModel)


class State:

    # storage mechanism is { name: Model }
    _ssm: Dict[int, SSM] = {}
    state_lock = Lock()

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        self.state_lock.acquire()
        self._logger.debug("Acquired state lock. Lock state: %s", self.state_lock.locked())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state_lock.release()
        self._logger.debug("Released state lock. Lock state: %s", self.state_lock.locked())

    def load(self, model: _T) -> _T:
        """
        Load state model into state registry

        :param model: state model
        :type model: StateModel
        """
        model.load()
        try:
            serialized_model = model.serialize()
        except AttributeError as exc:
            raise UninitializedStateError from exc
        else:
            self._ssm[model.__typehash__()] = SSM[_T](model)
            self._logger.info("Loaded state model: %s", pformat(serialized_model))
        return model

    def checkout(self, state_type: Type[_T]) -> _T:
        """
        Returns a deepcopy of requested state model

        :param state_type: 
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
        # do not trust any external pass-by-reference objects!
        state = copy.deepcopy(state)
        self._logger.info("Committing state model of type %s with cache mode: %s",
            type(state), "enabled" if cache else "disabled")
        # automatic type inference by typehash
        _type_hash = state.__typehash__() 
        self._logger.debug("Computed type hash: %s", _type_hash)
        # verify typehash exists in ssm registry
        if _type_hash not in self._ssm:
            self._logger.error("Committed typehash: %s did not match any state model", _type_hash)
            raise HashNotFound
        ssm = self._ssm[_type_hash]
        ssm.ref = state
        if len(ssm.queue) > 0:
            self._logger.debug("Executing asynchronous callback queue")
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
        Reset all loaded state models and clear cached documents
        """
        for _, ssm in self._ssm.items():
            ssm.ref.clear()
        self._ssm.clear()
        self._logger.debug("Reset system state")
