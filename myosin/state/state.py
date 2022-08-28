# -*- coding: utf-8 -*-
"""
State Context Manager 
=====================
"""

import copy
import asyncio
import logging
from typing import Dict, Type, TypeVar, Callable

from myosin.state.ssm import SSM
from myosin.typing import AsyncCallback
from myosin.utils.funcs import pformat
from myosin.utils.metrics import Metrics as metrics
from myosin.models.state import StateModel
from myosin.exceptions.state import ModelNotFound, UninitializedStateError

# generic runtime model type
_T = TypeVar('_T', bound=StateModel)


class State:
    """
    State access context manager. Request mutex locks on one or multiple state models by passing
    the model class in the initializer. Avoid nested context manager entry.

    .. code-block:: python

        with State(Model) as state:
            model = state.checkout(Model)
            ...
    """

    # shared state memory
    _ssm: Dict[int, SSM] = {}

    def __init__(self, *args: Type[_T]) -> None:
        self._logger = logging.getLogger(__name__)
        # use set to ensure locking accessors are mutually exclusive
        self.accessors = {self._ssm[hash(arg)] for arg in args}

    def __enter__(self):
        metrics.active_contexts.inc()
        for accessor in self.accessors:
            accessor.lock.acquire()
            self._logger.info("Acquired %s state lock", accessor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for accessor in self.accessors:
            accessor.lock.release()
            self._logger.info("Released %s state lock", accessor)
        metrics.active_contexts.dec()

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
        :raises ModelNotFound: if the requested state type does not exist
        :return: deep copy of requested state model
        :rtype: _T
        """
        with metrics.checkout_latency.labels(f"{state_type.__qualname__}").time():
            self._logger.info("Checking out state model of type %s", state_type)
            _type_hash = hash(state_type)
            self._logger.debug("Computed type hash: %s", _type_hash)
            ssm = self._ssm.get(_type_hash)
            if not ssm:
                raise ModelNotFound
            _copy = copy.deepcopy(ssm.ref)
        return _copy

    def commit(self, state: _T, cache: bool = False) -> _T:
        """
        Commit new state to system state and update state subscriber callbacks

        :param state: modified copy of state
        :type state: _T
        :param cache: cache the state to disk once updated, defaults to False
        :type cache: bool, optional
        :raises ModelNotFound: if system state has no state registered of the requested type
        :return: updated system state reference
        :rtype: _T
        """
        with metrics.commit_latency.labels(f"{state.__class__.__qualname__}").time():
            # do not trust any external pass-by-reference objects!
            state = copy.deepcopy(state)
            self._logger.info("Committing state model of type %s with cache mode: %s",
                              type(state), "enabled" if cache else "disabled")
            # automatic type inference by typehash
            _type_hash = state.__typehash__()
            self._logger.debug("Computed type hash: %s", _type_hash)
            # verify typehash exists in ssm registry
            if _type_hash not in self._ssm:
                self._logger.error(
                    "Committed typehash: %s did not match any state model", _type_hash)
                raise ModelNotFound
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
            raise ModelNotFound
        ssm.queue.append(callback)

    def reset(self) -> None:
        """
        Reset all loaded state models and clear cached documents
        """
        for _, ssm in self._ssm.items():
            ssm.ref.clear()
        self._ssm.clear()
        self._logger.debug("Reset system state")
