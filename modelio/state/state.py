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
from typing import Any, Coroutine, Tuple, Type, TypeVar, Callable, List, Union

# generic runtime model type
_T = TypeVar('_T', bound=StateModel)

class StateManager:

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): ...

    def _load_runtime_models(self) -> None: ...

    def commit(self, state: StateModel, source: bool = False, cache: bool = True) -> bool:
        """
        Commiting a state variable change requires up to 3 steps:
          1. Independant system validation (for external system state changes)
          2. Update state variable in runtime layer (here)
          3. Notify subscribers of state change
        :param state: proposed state variable change
        :type state: StateModel
        :param source: flag indicating the source module is pushing these changes (do not call validator)
        :type source: bool
        :param cache: flag which indicates the commit should update the system cache, defaults to True
        :type cache: bool, optional
        :return: commit status
        :rtype: bool
        """
        # cache old model
        cached = copy.deepcopy(self.state)
        # await update state
        self.experiment = state
        # async update subscribers
        asyncio.run(self._subscriber_runner(state, cr.experiment))
        for _property in cr.experiment_properties.keys():
            if getattr(cached, _property) != getattr(state, _property):
                asyncio.run(self._subscriber_runner(
                    state, cr.experiment_properties[_property]))
        self._logger.info("State change commit for %s successful", state)
        return True

    def subscribe(self, state_type: Type[_T], callback: Callable[[_T], Coroutine[Any, Any, None]]) -> None:
        """
        Subscribe an asynchronous state change listener to a designated runtime model
        :param state_type: runtime type to subscribe to
        :type state_type: Type[T]
        :param callback: state change listener callback
        :type callback: Callable[[T], Coroutine[Any, Any, None]]
        """

    def subscribe_property(self, state_type: Type[_T], _property: str, callback: Callable[[_T],
                           Coroutine[Any, Any, None]]) -> None:
        """
        Subscribe an asynchronous state change listener to a designated runtime model property
        :param state_type: runtime type to subscribe to
        :type state_type: Type[_T]
        :param _property: property to subscribe to
        :type _property: str
        :param callback: state change listener callback
        :type callback: Callable[[_T], Coroutine[Any, Any, None]]
        :raises RuntimeError: if the requested property does not exist in the provided state
        """
        if not hasattr(state_type, _property):
            raise RuntimeError
        if state_type is ImagingProfile: prop_callbacks = cr.ip_properties
        elif state_type is Device: prop_callbacks = cr.device_properties
        elif state_type is Protocol: prop_callbacks = cr.protocol_properties
        elif state_type is Experiment: prop_callbacks = cr.experiment_properties
        else: prop_callbacks = cr.icb_properties
        if _property in prop_callbacks.keys():
            prop_callbacks[_property].append(callback)
        else:
            prop_callbacks[_property] = [callback]

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
