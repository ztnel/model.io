
import time
import asyncio
import logging
import random

from typing import NoReturn
from myosin import State
from example.models import Telemetry
from example.models import System


class MQTTHandler:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        with State(Telemetry) as state:
            state.subscribe(Telemetry, self.report_telemetry)
            state.subscribe(Telemetry, self.report_test)

    async def report_telemetry(self, telemetry: Telemetry) -> None:
        self._logger.info(" ++++ CALLBACK Telemetry: %s", telemetry)

    async def report_test(self, telemetry: Telemetry) -> None:
        self._logger.info(" ++++ CALLBACK TEST")

    def report_loop(self) -> NoReturn:
        while True:
            time.sleep(1)
            with State(Telemetry) as state:
                telemetry = state.checkout(Telemetry)
            try:
                self._logger.info(f"Telemetry report: {telemetry}")
                rc = random.randint(0, 1)
                if rc:
                    raise ConnectionError
            except ConnectionError as exc:
                self._logger.exception("Failed to write to stream: %s", exc)
                with State(System) as state:
                    system = state.checkout(System)
                    system.online = False
                    state.commit(system, cache=True)
            else:
                with State(System) as state:
                    system = state.checkout(System)
                    system.online = True
                    state.commit(system, cache=True)


    async def async_loop(self) -> NoReturn:
        while True:
            await asyncio.sleep(1)
            try:
                if random.randint(0, 1):
                    raise ConnectionError
            except ConnectionError as exc:
                self._logger.exception("Failed to write to stream: %s", exc)
                with State(System) as state:
                    system = state.checkout(System)
                    system.online = False
                    state.commit(system, cache=True)
            else:
                with State(System) as state:
                    system = state.checkout(System)
                    system.online = True
                    state.commit(system, cache=True)
