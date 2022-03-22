import os
import logging
from typing import Any, Dict
from datetime import datetime

from myosin import _PKey
from myosin import StateModel
from myosin import State


class User(StateModel):

    def __init__(self, _id: _PKey) -> None:
        super().__init__(_id)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, email: str) -> None:
        self.__email = email

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

    def deserialize(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


class Telemetry(StateModel):

    def __init__(self, _id: _PKey) -> None:
        super().__init__(_id)

    @property
    def tp(self) -> float:
        return self.__tp

    @tp.setter
    def tp(self, value: float) -> None:
        self.__tp = value

    @property
    def timestamp(self) -> float:
        return datetime.now().timestamp()

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'temp': self.tp,
            'timestamp': self.timestamp
        }

    def deserialize(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if k == "timestamp":
                continue
            setattr(self, k, v)


if __name__ == "__main__":
    os.environ['MYOSIN_CACHE_BASE_PATH'] = "tests/cache"
    logging.basicConfig(level=logging.DEBUG)
    _log = logging.getLogger(__name__)

    u = User(_id=1)
    u.deserialize(**{'name': "chris", 'email': "chris@email.io"})
    t = Telemetry(_id=1)
    t.deserialize(**{'tp': 65.0})
    u.email = "bad"
    _log.info(u)

    with State() as state:
        state.load(u)
        state.load(t)

    with State() as state:
        user = state.checkout(User)
        _log.info(user.email)

    with State() as state:
        user = state.checkout(User)
        user.email = "bad@email.com"
        state.commit(user, cache=True)

    with State() as state:
        user = state.checkout(User)
        _log.info(user)

    with State() as state:
        telemetry = state.checkout(Telemetry)
        _log.info(telemetry)

    with State() as state:
        telemetry = state.checkout(Telemetry)
        telemetry.tp = 45.0
        state.commit(telemetry, cache=True)
