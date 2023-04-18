
import asyncio
import logging
import random

from myosin.core import State
from integration.models import TemperatureController
from myosin.core.event import StateEvent as se


class MQTTHandler:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        with State(TemperatureController) as state:
            state.subscribe(TemperatureController, event=se.REPORTED,
                            callback=self.report_telemetry)

    async def report_telemetry(self, telemetry: TemperatureController, delta: dict) -> None:
        self._logger.info(" ++++ CALLBACK Telemetry: %s", telemetry)

    async def process_command(self) -> None:
        while True:
            await asyncio.sleep(3)
            with State(TemperatureController) as state:
                tc = state.checkout(TemperatureController)
                tc.setpoint = random.uniform(10.5, 75.5)
                state.commit(tc, cache=True, event=se.DESIRED)
