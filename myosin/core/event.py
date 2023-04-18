
from enum import IntEnum
from typing import Any, Callable, Coroutine, Generic, TypeVar

from myosin.core.model import StateModel

_S = TypeVar('_S', bound=StateModel)


class ReconPolicy(IntEnum):
    NEVER = 0
    ONCE = 1
    ALWAYS = 2


class StateEvent(IntEnum):
    DESIRED = 0
    REPORTED = 1


class Event(Generic[_S]):

    def __init__(self, policy: ReconPolicy, callback) -> None:
        self.executions = 0
        self.policy = policy
        self.callback = callback

    @property
    def policy(self) -> ReconPolicy:
        return self.__policy

    @policy.setter
    def policy(self, policy: ReconPolicy) -> None:
        self.__policy = policy

    @property
    def callback(self) -> Callable[[_S, dict], Coroutine[Any, Any, None]]:
        return self.__callback

    @callback.setter
    def callback(self, callback: Callable[[_S, dict], Coroutine[Any, Any, None]]) -> None:
        self.__callback = callback
