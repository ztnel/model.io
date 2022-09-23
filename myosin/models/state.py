# -*- coding: utf-8 -*-
"""
State Model
===========

System state model base class.

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

import os
import json
import uuid
import logging
from json import JSONDecodeError
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from myosin.typing import PrimaryKey
from myosin.utils.funcs import pformat
from myosin.utils.metrics import Metrics as metrics
from myosin.exceptions.cache import CachePathError, NullCachePathError

BP_ENV_VAR = "MYOSIN_CACHE_BASE_PATH"


class StateModel(ABC):
    """
    System state model base class. Provides methods and properties required for use with the global
    state context manager. Define a custom model by implementing this class and providing
    overrides for the :func:`~StateModel.serialize` and :func:`~StateModel.deserialize` methods.

    .. code-block:: python

        class Telemetry(StateModel):

            def __init__(self) -> None:
                super().__init__()
                self.temperature = 25.5
                self.timestamp = datetime.now().timestamp()

            @property
            def temperature(self) -> float:
                return self.__temperature

            @temperature.setter
            def temperature(self, value: float) -> None:
                self.__temperature = value

            @property
            def timestamp(self) -> float:
                return  self.__timestamp

            @timestamp.setter
            def timestamp(self, value: float) -> None:
                self.__timestamp = value

            def serialize(self) -> Dict[str, Any]:
                return {
                    'id': self.id,
                    'temperature': self.temperature,
                    'timestamp': self.timestamp
                }

            def deserialize(self, **kwargs) -> None:
                for k, v in kwargs.items():
                    setattr(self, k, v)
    """

    def __init__(self, _id: Optional[PrimaryKey] = None) -> None:
        self._logger = logging.getLogger(__name__)
        if _id is None:
            _id = str(uuid.uuid4())
        self.id = _id
        self.cache_base_path = os.environ.get(BP_ENV_VAR)
        self._cpath = f'{self.cache_base_path}/{self.__class__.__name__}.json'

    def __typehash__(self) -> int:
        """
        Get hash of state model type

        :return: hash of state model
        :rtype: int
        """
        return hash(type(self))

    def __hash__(self) -> int:
        """
        Get object hash

        :return: hash of python object
        :rtype: int
        """
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        # TODO: chance of collision if auto id is used (uuid4)
        if hasattr(o, 'id') and hasattr(self, 'id'):
            return o.id == self.id  # type: ignore
        return False

    def __repr__(self) -> str:
        return pformat(self.serialize())

    @property
    def id(self) -> PrimaryKey:
        """
        Get state model id

        :return: state model id
        :rtype: PrimaryKey
        """
        return self.__id

    @id.setter
    def id(self, _id: PrimaryKey) -> None:
        """
        Set state model id

        :param _id: state model id
        :type _id: PrimaryKey
        """
        self.__id = _id

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
        Load contents from json into :class:`~StateModel` using :func:`~StateModel.deserialize`.
        If document is not found, log a warning and continue. If the cached model fails to be read
        into the runtime context remove the document.
        """
        try:
            with open(self._cpath, 'r') as json_file:
                payload: Dict[str, Any] = json.load(json_file)
        except JSONDecodeError as exc:
            self._logger.error("Model cache document corrupt:\n%s", exc)
            self.clear()
        except FileNotFoundError:
            self._logger.warning("Model not found in caching directory")
        else:
            self.deserialize(**payload)
            self._logger.debug("Loaded state model: %s", self)

    def clear(self) -> None:
        """
        Remove the cached json file associated with this model
        """
        if os.path.exists(self._cpath):
            os.remove(self._cpath)
            self._logger.debug("Removed cached document: %s", self._cpath)

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize :class:`StateModel` properties keys and values into a python dictionary. 
        Key names should match :class:`StateModel` property names. This function must be overridden.

        .. code-block:: python

            def serialize(self) -> Dict[str, Any]:
                return {
                    'id': self.id,
                    'temperature': self.temperature,
                    'timestamp': self.timestamp
                }

        :raises NotImplementedError: if method is not overriden
        :return: serialized model as a python dictionary
        :rtype: Dict[str, Any]
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, **kwargs) -> None:
        """
        Deserialize :class:`StateModel` properties keys and values from kwargs generated by 
        :func:`StateModel.serialize` output. This function must be overridden.

        .. code-block:: python

            def deserialize(self, **kwargs) -> None:
                for k, v in kwargs.items():
                    setattr(self, k, v)

        :raises NotImplementedError: if method is not overriden
        """
        raise NotImplementedError
