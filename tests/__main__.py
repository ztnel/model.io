import logging
from typing import Any, Dict

from modelio import _PKey
from modelio import StateModel
from modelio import State


class User(StateModel):

    def __init__(self, _id: _PKey, name: str) -> None:
        super().__init__(_id, name)

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _log = logging.getLogger(__name__)

    u = User(_id=1, name='user')
    u.email = "bad"
    _log.info(u)

    with State() as state:
        state.load(u)

    with State() as state:
        user = state.checkout(User)
        _log.info(user.email)

    with State() as state:
        user = state.checkout(User)
        user.email = "bad@email.com"
        state.commit(user)

    with State() as state:
        user = state.checkout(User)
        _log.info(user.email)

    _log.info(user)
