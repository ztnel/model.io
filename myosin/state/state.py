# -*- coding: utf-8 -*-
"""
State Manager
=============
Modified: 2021-05
Dependancies
------------
```
import logging
import asyncio
from monitor.models.icb import ICB
from monitor.models.device import Device
from monitor.models.protocol import Protocol
from monitor.models.experiment import Experiment
from monitor.models.imaging_profile import ImagingProfile
```
"""
import copy
import logging
import asyncio
import traceback
from typing import Any, Coroutine, Dict, Tuple, Type, TypeVar, Callable, List
from myosin.utils.funcs import pformat
from myosin.utils.concurrency import ThreadUtils as tutils
from myosin.exceptions.state import NullCheckoutError
from myosin.models.state import StateModel

# generic runtime model type
_T = TypeVar('_T', bound=StateModel)


class State:

    # storage mechanism is { name: Model }
    _ssm: Dict[int, Any] = {}

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
        self._ssm[model.__typehash__()] = model
        self._logger.info("Loaded state model: %s", pformat(model.serialize()))
        return model

    @tutils.lock(tutils.state_lock)
    def checkout(self, _type: Type[_T]) -> _T:
        """
        Returns requested state model

        :return: deep copy of requested state model
        :rtype: StateModel
        """
        self._logger.info("Checking out state model of type %s", _type)
        _type_hash = hash(_type)
        self._logger.debug("Computed type hash: %s", _type_hash)
        mdl = self._ssm.get(_type_hash)
        if not mdl:
            raise NullCheckoutError
        return copy.deepcopy(mdl)

    @tutils.lock(tutils.state_lock)
    def commit(self, state: _T, cache: bool = False) -> _T:
        _type_hash = hash(type(state))
        self._ssm[_type_hash] = state
        if cache:
            state.cache()
            self._logger.debug("Cached commited state model %s", state)
        return state

    def subscribe(self, state_type: Type[_T], callback: Callable[[_T], Coroutine[Any, Any, None]]) -> None:
        """
        Subscribe an asynchronous state change listener to a designated runtime model

        :param state_type: runtime type to subscribe to
        :type state_type: Type[T]
        :param callback: state change listener callback
        :type callback: Callable[[T], Coroutine[Any, Any, None]]
        """

    async def _subscriber_runner(self, state_var: _T,
                                 registry: List[Callable[[_T], Coroutine[Any, Any, None]]]) -> None:
        """
        Async runner that executes all subscriber coroutines with new runtime model state changes.

        :param state_var: pre-validated runtime model to pass to subscribers
        :type state_var: T
        :param registry: list of subscriber coroutines
        :type registry: List[Callable[[T], Awaitable[None]]]
        """
        # construct coroutine lists
        tasks = [subscriber(state_var) for subscriber in registry]
        # return results from coroutines with exceptions if any
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # reformat tasks to display only the name
        operations = tuple(zip(map(lambda x: x.__qualname__, tasks), results))
        self._logger.debug("%s Subscriber operations: %s", type(state_var).__name__, operations)
        # filter by operations which yielded an exception
        exceptions: List[Tuple[str, Exception]] = list(
            filter(lambda x: x[1] is not None, operations))
        for func, exc in exceptions:
            self._logger.exception("Subscriber function: %s encountered an exception: %s", func,
                                   "".join(traceback.format_exception(
                                       etype=type(exc), value=exc, tb=exc.__traceback__
                                   )))
