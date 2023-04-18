
import asyncio
import random
import time
import logging
from asyncio import Queue
from typing import NoReturn
from myosin.core import State
from integration.models import TemperatureController
from myosin.core.event import StateEvent as se


class DeviceController:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self.setpoint = 25.0
        with State(TemperatureController) as state:
            # subscribe to TemperatureController
            state.subscribe(TemperatureController, event=se.DESIRED, callback=self.digest_command)

    async def digest_command(self, t: TemperatureController, delta: dict) -> None:
        self._logger.info("+++++++++ CALLBACK: digest %s", delta)
        await self.setpoint_queue.put(t.setpoint)

    async def command_loop(self, setpoint_queue: Queue[float]) -> NoReturn:
        while True:
            self._logger.info("Waiting for new setpoint command")
            setpoint = await setpoint_queue.get()
            self._logger.info("Got new setpoint command")
            self.set_setpoint(setpoint)

    async def report_loop(self) -> NoReturn:
        while True:
            # perform device I/O operations outside the context manager to reduce the amount of time in critical section
            temp = self.get_temperature()
            setp = self.get_setpoint()
            with State(TemperatureController) as state:
                # checkout current reported state
                tc = state.checkout(TemperatureController)
                # update reported state fields
                tc.temperature = temp
                tc.setpoint = setp
                tc.timestamp = time.time()
                # commit to system state as a new reported event
                state.commit(tc, event=se.REPORTED, cache=True)
            await asyncio.sleep(1)

    async def main(self) -> None:
        loop = asyncio.get_running_loop()
        loop.set_debug(True)
        self.setpoint_queue = Queue[float]()
        await asyncio.gather(
            *[
                loop.create_task(self.report_loop(), name="report"),
                loop.create_task(self.command_loop(self.setpoint_queue), name="command")
            ]
        )

    def get_temperature(self) -> float:
        return random.uniform(10.5, 75.5)

    def get_setpoint(self) -> float:
        return self.setpoint

    def set_setpoint(self, setpoint: float) -> None:
        self._logger.info("+++++++++ TC setpoint sent: %s", setpoint)
        self.setpoint = setpoint
