import asyncio
import os
import sys
import time
import logging

from prometheus_client import start_http_server
from threading import Thread
from myosin import State

from example.models import Telemetry
from example.cloud.mqtt import MQTTHandler
from example.models.system import System
from example.sensors.uart import UARTInterface



def synchronous(mqtt: MQTTHandler, sensors:UARTInterface):
    mqtt_runner = Thread(target=mqtt.report_loop, args=(), daemon=True)
    uart_runner = Thread(target=sensors.report_loop, args=(), daemon=True)
    uart_runner.start()
    mqtt_runner.start()
    while True:
        if not mqtt_runner.is_alive():
            _log.critical("MQTT runner exited")
            sys.exit(1)
        if not uart_runner.is_alive():
            _log.critical("UART runner exited")
            sys.exit(1)
        time.sleep(1)


async def asynchronous(mqtt:MQTTHandler, sensors:UARTInterface):
    loop = asyncio.get_running_loop()
    tasks = [
        loop.create_task(mqtt.async_loop()),
        loop.create_task(sensors.async_report_loop())
    ]
    await asyncio.gather(*tasks)


os.environ['MYOSIN_CACHE_BASE_PATH'] = "example/tmp"
logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger(__name__)



t = Telemetry()
s = System()

with State() as state:
    state.load(t)
    state.load(s)

start_http_server(8000)
mqtt = MQTTHandler()
sensors = UARTInterface()
asyncio.run(asynchronous(mqtt, sensors))
# synchronous(mqtt, sensors)
