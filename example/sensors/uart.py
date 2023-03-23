
import asyncio
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
            time.sleep(1)
            reading = random.uniform(10.5, 75.5)
            with State(Telemetry) as state:
                telemetry = state.checkout(Telemetry)
                telemetry.tp = reading
                state.commit(telemetry, cache=True)
            self._logger.info("Telemetry report: %s", telemetry)

    async def async_report_loop(self) -> NoReturn:
        while True:
            await asyncio.sleep(1)
            reading = random.uniform(10.5, 75.5)
            with State(Telemetry) as state:
                telemetry = state.checkout(Telemetry)
                telemetry.tp = reading
                state.commit(telemetry, cache=True)
            self._logger.info("Telemetry report: %s", telemetry)
