# -*- coding: utf-8 -*-
"""
State Model
===========

"""

import os
import json
from json import JSONDecodeError
from typing import Any, Dict, Optional

from myosin.typing import _PKey
from myosin.utils.metrics import Metrics as metrics
from myosin.models.base import BaseModel
from myosin.exceptions.cache import CachePathError, NullCachePathError

BP_ENV_VAR = "MYOSIN_CACHE_BASE_PATH"


class StateModel(BaseModel):
    """
    System state model for categorical and homogenous data access.
    """

    def __init__(self, _id: Optional[_PKey] = None) -> None:
        super().__init__(_id)
        self.cache_base_path = os.environ.get(BP_ENV_VAR)
        self._cpath = f'{self.cache_base_path}/{self.__class__.__name__}.json'

    def cache(self) -> None:
        """
        Serialize contents and save to cache as a json file

        :raises NullCachePathError: if cache base path is not set 
        :raises CachePathError: if cache base path is not valid
        """
        with metrics.cache_latency.labels(f"{self.__class__.__name__}").time():
            if not self.cache_base_path:
                raise NullCachePathError(
                    f"Caching basepath is unset. set the {BP_ENV_VAR} environment variable before using model caching")
            if not os.path.exists(self.cache_base_path):
                raise CachePathError(f"Caching base path {self.cache_base_path} does not exist")
            with open(self._cpath, 'w+') as json_file:
                cached_payload = self.serialize()
                json.dump(cached_payload, json_file)
            self._logger.debug("Cached state model: %s", self)

    def load(self) -> None:
        """
        Load contents from json into state model
        """
        try:
            with open(self._cpath, 'r') as json_file:
                device_payload: Dict[str, Any] = json.load(json_file)
        except JSONDecodeError as exc:
            self._logger.error("Model cache document corrupt:\n%s", exc)
            self.clear()
        except FileNotFoundError:
            self._logger.warning("Model not found in caching directory")
        else:
            self.deserialize(**device_payload)
            self._logger.debug("Loaded state model: %s", self)

    def clear(self) -> None:
        """
        Remove the cached json file associated with this model
        """
        if os.path.exists(self._cpath):
            os.remove(self._cpath)
            self._logger.debug("Removed cached document: %s", self._cpath)
