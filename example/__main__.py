import os
import logging
from example.models import Telemetry

from myosin import State


os.environ['MYOSIN_CACHE_BASE_PATH'] = "tests/cache"
logging.basicConfig(level=logging.DEBUG)
# _log = logging.getLogger(__name__)


t = Telemetry()


with State() as state:
    state.load(t)
