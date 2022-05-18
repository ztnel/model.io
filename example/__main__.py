import os
import time
import logging

from myosin import State
from threading import Thread
from example.models import Telemetry
from example.cloud.mqtt import MQTTHandler
from example.models.system import System
from example.sensors.uart import UARTInterface


os.environ['MYOSIN_CACHE_BASE_PATH'] = "example/cache"
logging.basicConfig(level=logging.DEBUG)
# _log = logging.getLogger(__name__)


t = Telemetry()
s = System()

with State() as state:
    state.load(t)
    state.load(s)

mqtt = MQTTHandler()
sensors = UARTInterface()
Thread(target=mqtt.report_loop, args=(), daemon=True).start()
Thread(target=sensors.report_loop, args=(), daemon=True).start()

while True:
    time.sleep(10)
