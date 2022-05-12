from datetime import datetime
from typing import Any, Dict
from myosin import StateModel


class Telemetry(StateModel):

    def __init__(self) -> None:
        super().__init__()

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
