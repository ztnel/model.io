
import time
import random
import logging
from typing import NoReturn
from myosin import State
from example.models import Telemetry


class UARTInterface:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def report_loop(self) -> NoReturn:
        while True:
            time.sleep(0.01)
            reading = random.uniform(10.5, 75.5)
            with State() as state:
                telemetry = state.checkout(Telemetry)
                telemetry.tp = reading
                state.commit(telemetry, cache=True)
            with State() as state:
                telemetry = state.checkout(Telemetry)
            assert(telemetry.tp ==reading)
            self._logger.info("Telemetry report: %s", telemetry)
