import asyncio
import os
import logging
from threading import Thread
from myosin.core import State
from prometheus_client import start_http_server
from integration.mqtt import MQTTHandler
from integration.models import TemperatureController
from integration.device import DeviceController


os.environ['MYOSIN_CACHE_BASE_PATH'] = "integration/tmp"
logging.basicConfig(level=logging.INFO)


def threaded() -> None:
    asyncio.run(mqtt.process_command())


t = TemperatureController()

with State() as state:
    state.load(t)

start_http_server(8000)
mqtt = MQTTHandler()
dc = DeviceController()
Thread(target=threaded).start()

asyncio.run(dc.main(), debug=True)
