
import time

import logging
from typing import NoReturn
from myosin import State
from example.models import Telemetry
from example.models import System


class Runner:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def report_loop(self) -> NoReturn:
        while True:
            time.sleep(0.1)
            with State() as state:
                telemetry = state.checkout(Telemetry)
            try:
                print(f"Telemetry report: {telemetry}")
            except ConnectionError as exc:
                self._logger.exception("Failed to write to stream: %s", exc)
                with State() as state:
                    system = state.checkout(System)
                    system.online = False
                    state.commit(system, cache=True)
