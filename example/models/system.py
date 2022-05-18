from typing import Any, Dict
from myosin import StateModel


class System(StateModel):

    def __init__(self) -> None:
        super().__init__()
        self.online = False

    @property
    def online(self) -> bool:
        return self.__online

    @online.setter
    def online(self, status: bool) -> None:
        self.__online = status

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'online': self.online
        }

    def deserialize(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
