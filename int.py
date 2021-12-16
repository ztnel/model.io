from typing import Any, Dict
from modelio import _PKey
from modelio.models.state import StateModel
from modelio.state import StateIO


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


u = User(_id=1, name='user')
u.email = "bad"
print(u)

with StateIO() as state:
    state.load(u)

with StateIO() as state:
    user = state.checkout('user', User)
    user.email = 'help@mail.com'
print(user)
