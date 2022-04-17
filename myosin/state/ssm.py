# -*- coding: utf-8 -*-

import logging
import asyncio
import traceback
from typing import Generic, List, Tuple, TypeVar, Callable

from myosin.models.state import StateModel
from myosin.typing import AsyncCallback


_S = TypeVar('_S', bound=StateModel)


class SSM(Generic[_S]):

    def __init__(self, reference: _S) -> None:
        self._logger = logging.getLogger(__name__)
        self.ref = reference
        self.queue = []

    @property
    def refhash(self) -> int:
        return hash(self.__ref)

    @property
    def typehash(self) -> int:
        return self.ref.__typehash__()

    @property
    def ref(self) -> _S:
        return self.__ref

    @ref.setter
    def ref(self, model: _S) -> None:
        self.__ref = model

    @property
    def queue(self) -> List[Callable[[_S], AsyncCallback]]:
        return self.__queue

    @queue.setter
    def queue(self, queue: List[Callable[[_S], AsyncCallback]]) -> None:
        self.__queue = queue

    async def execute(self) -> None:
        """
        Executes all subscriber coroutines with new model reference.
        """
        # construct coroutine lists
        tasks = [callback(self.ref) for callback in self.queue]
        # return results from coroutines with exceptions if any
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # reformat tasks to display only the name
        operations = tuple(zip(map(lambda x: x.__qualname__, tasks), results))
        self._logger.debug("%s Subscriber operations: %s", type(self.ref).__name__, operations)
        # filter by operations which yielded an exception
        exceptions: List[Tuple[str, Exception]] = list(
            filter(lambda x: type(x[1]) is BaseException, operations))
        for func, exc in exceptions:
            self._logger.exception("Subscriber function: %s encountered an exception: %s", func,
                                   "".join(traceback.format_exception(
                                       etype=type(exc), value=exc, tb=exc.__traceback__
                                   )))
