# -*- coding: utf-8 -*-
"""
Myosin State Subscription Model
===============================

Modified: 2022-08

Registered system state model wrapper.

"""

import logging
import asyncio
import traceback
from threading import Lock
from typing import Generic, Tuple, TypeVar
from asyncio.events import AbstractEventLoop
from myosin.core.event import EType, Event

from myosin.utils.metrics import Metrics as metrics
from myosin.core.model import StateModel


_S = TypeVar('_S', bound=StateModel)


class SSM(Generic[_S]):

    def __init__(self, reference: _S) -> None:
        self._logger = logging.getLogger(__name__)
        self.desired = reference
        self.reported = reference
        self.lock = Lock()
        self.event_queue: list[Event[_S]] = []

    def __str__(self) -> str:
        return f"{self.reported.__class__.__qualname__}"

    @property
    def lock(self) -> Lock:
        return self.__lock

    @lock.setter
    def lock(self, lock: Lock) -> None:
        self.__lock = lock

    @property
    def refhash(self) -> int:
        return hash(self.__reported)

    @property
    def typehash(self) -> int:
        return self.reported.__typehash__()

    @property
    def desired(self) -> _S:
        return self.__desired

    @desired.setter
    def desired(self, model: _S) -> None:
        self.__desired = model

    @property
    def reported(self) -> _S:
        return self.__reported

    @reported.setter
    def reported(self, model: _S) -> None:
        self.__reported = model

    @property
    def delta(self) -> dict:
        return self._filter_delta(self.reported.serialize(), self.desired.serialize())

    def resolve_desired(self, state: _S) -> None:
        desired_events = list(filter(lambda x: x.etype == EType.DESIRED, self.event_queue))
        self.desired = state
        if self.delta == {}:
            # send notification of reconcilation and return
            self._logger.debug("Reconciled desired changes for state model: %s", state)
            return
        # have deltas to resolve
        # get all property level desired events
        queued_events = []
        prop_desired_events = list(filter(lambda x: x.prop != None, desired_events))
        for k, v in self.delta.items():
            if k in [x.prop for x in prop_desired_events]:
                queued_events.append()
        # perform policy checks

        # if policy not met failed reset desired to reported to reconcile

        if len(desired_events) > 0:
            self._logger.debug("Executing asynchronous callback queue")
            self._execute(events)

    def resolve_reported(self, state: _S) -> None:
        reported_events = list(filter(lambda x: x.etype == EType.REPORTED, self.event_queue))
        self.reported = state
        if self.delta == {}:
            # send notification of reconcilation and return
            self._logger.debug("Reconciled desired changes for state model: %s", state)
            return
        if len(reported_events) > 0:
            self._logger.debug("Executing asynchronous callback queue")
            self._execute(events)

    def _execute(self, events: list[Event]) -> None:
        """
        Schedule callbacks for either synchronous and asynchrounous runtimes.
        """
        loop = self._get_asyncio_ctx()
        if loop.is_running():
            self._logger.debug("Loop is running schedule callbacks")
            loop.create_task(self.cb_runner(events), name=f"cb_runner_{self}")
            return
        self._logger.debug("Loop is not running, start event loop and schedule callbacks")
        try:
            loop.run_until_complete(self.cb_runner(events))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def cb_runner(self, events: list[Event]) -> None:
        """
        Executes all subscriber coroutines with new model reference.
        """
        tasks = [event.callback(self.reported) for event in events]
        # return results from coroutines with exceptions if any
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # increment execution counters
        for event in events:
            event.executions += 1
        # reformat tasks to display only the name
        operations = tuple(zip(map(lambda x: x.__qualname__, tasks), results))
        self._logger.debug("%s Subscriber operations: %s", type(self.reported).__name__, operations)
        # filter by operations which yielded an exception
        exceptions: list[Tuple[str, Exception]] = list(
            filter(lambda x: type(x[1]) is BaseException, operations))
        for func, exc in exceptions:
            # track aggregate exceptions
            metrics.exc_count.labels(str(self)).inc()
            self._logger.exception("Subscriber function: %s encountered an exception: %s", func,
                                   "".join(traceback.format_exception(
                                       etype=type(exc), value=exc, tb=exc.__traceback__
                                   )))

    def _get_asyncio_ctx(self) -> AbstractEventLoop:
        """
        Return running event loop if available otherwise build new event loop using default policy
        """
        try:
            loop = asyncio.get_running_loop()
            self._logger.debug("Detected running event loop.")
        except RuntimeError:
            self._logger.debug(
                "No running event loop detected. Creating new event loop using default policy.")
            loop = asyncio.new_event_loop()
        return loop

    def _filter_delta(self, reported: dict, desired: dict) -> dict:
        """
        Recursive method to compare a cached dict to an incoming dict and generating a dict with
        undiscovered changes from the incoming with respect to the cached copy.

        :param cache: reference delta diff
        :type cache: dict
        :param delta: incoming delta
        :type delta: dict
        :return: dict containing only new updates from delta
        :rtype: dict
        """
        _delta = {}
        # iterate through layer items
        for kvp in desired.items():
            key, value = kvp
            # check for new keys
            if key not in reported.keys():
                _delta[key] = value
            # explore nested structures
            elif isinstance(value, dict):
                diff = self._filter_delta(reported[key], desired[key])
                if diff != {}: _delta[key] = diff
            # check for value diffs
            elif reported[key] != desired[key]:
                _delta[key] = desired[key]
        return _delta
