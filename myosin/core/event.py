
from enum import IntEnum
from typing import Any, Callable, Coroutine, Generic, TypeVar

from myosin.core.model import StateModel

_S = TypeVar('_S', bound=StateModel)


class ReconPolicy(IntEnum):
    NEVER = 0
    ONCE = 1
    ALWAYS = 2


class EType(IntEnum):
    DESIRED = 0
    REPORTED = 1


class Event(Generic[_S]):

    def __init__(self) -> None:
        self.executions = 0

    @property
    def etype(self) -> EType:
        return self.__etype

    @etype.setter
    def etype(self, etype: EType) -> None:
        self.__etype = etype

    @property
    def prop(self) -> property:
        return self.__prop

    @prop.setter
    def prop(self, prop: property) -> None:
        self.__prop = prop

    @property
    def policy(self) -> ReconPolicy:
        return self.__policy

    @policy.setter
    def policy(self, policy: ReconPolicy) -> None:
        self.__policy = policy

    @property
    def callback(self) -> Callable[[_S], Coroutine[Any, Any, None]]:
        return self.__callback

    @callback.setter
    def callback(self, callback: Callable[[_S], Coroutine[Any, Any, None]]) -> None:
        self.__callback = callback
