from myosin import StateModel
from typing import Any, Dict


SERIALIZED_MODEL = {
    'id': 1,
    'name': "cS",
    'email': "chris@email.com"
}


class DemoState(StateModel):

    def __init__(self, _id) -> None:
        super().__init__(_id)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name
        }

    def deserialize(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
