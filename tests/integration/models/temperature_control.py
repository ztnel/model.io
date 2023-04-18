import time
from typing import Any, Dict
from myosin.core import StateModel


class TemperatureController(StateModel):

    DEFAULT_TP = 25.5
    DEFAULT_SETPOINT = 25.0

    def __init__(self, temp: float = DEFAULT_TP, setpoint: float = DEFAULT_SETPOINT) -> None:
        super().__init__()
        self.temperature = temp
        self.setpoint = setpoint
        self.timestamp = time.time()

    @property
    def temperature(self) -> float:
        return self.__temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.__temperature = value

    @property
    def setpoint(self) -> float:
        return self.__setpoint

    @setpoint.setter
    def setpoint(self, value: float) -> None:
        self.__setpoint = value

    @property
    def timestamp(self) -> float:
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value: float) -> None:
        self.__timestamp = value

    def serialize(self) -> Dict[str, Any]:
        return {
            'temperature': self.temperature,
            'setpoint': self.setpoint,
            'timestamp': self.timestamp
        }

    def deserialize(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
