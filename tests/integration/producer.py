from datetime import datetime
import time
import random

from myosin import State


class Point:

    @property
    def tc(self) -> float:
        return random.uniform(0, 40)

    @property
    def timestamp(self) -> float:
        return datetime.now().timestamp()


class Producer:

    def __init__(self) -> None:
        with State() as state:
            pass

    def run(self, rate: int) -> None:
        delay = 1 / rate
        while True:
            Point()
            time.sleep(delay)
