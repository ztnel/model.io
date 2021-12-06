# -*- coding: utf-8 -*-
"""
State Model Abstract
====================
Modified: 2021-12

Dependencies:
-------------
```
```
"""

import os
import json
from json import JSONDecodeError
from typing import Any, Dict
from modelio.typing import _PKey
from modelio.models.base import BaseModel


class StateModel(BaseModel):

    def __init__(self, _id: _PKey, name: str) -> None:
        super().__init__(_id)
        self.name = name
        cache_base_path = os.environ.get('MODELIO_CACHE_BASE_PATH')
        # resolved path name includes model name and id
        self._cpath = f'{cache_base_path}/{self.name}-{self.id}'

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    def cache(self) -> None:
        """
        Serialize contents and save to cache as a json file
        """
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
        except FileNotFoundError:
            self._logger.warning("Model not found in caching directory")
        else:
            self.deserialize(**device_payload)
            self._logger.debug("Loaded state model: %s", self)
