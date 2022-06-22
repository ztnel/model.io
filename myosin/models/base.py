# -*- coding: utf-8 -*-
"""
Base Model Abstract
===================
Modified: 2022-03
"""

import logging
import uuid
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

from myosin.typing import _PKey
from myosin.utils.funcs import pformat


class BaseModel(ABC):

    def __init__(self, _id: Optional[_PKey] = None) -> None:
        self._logger = logging.getLogger(__name__)
        if not _id:
            _id = str(uuid.uuid4())
        self.id = _id

    def __typehash__(self) -> int:
        return hash(type(self))

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        # NOTE: chance of collision if auto id is used (uuid4)
        if hasattr(o, 'id') and hasattr(self, 'id'):
            return o.id == self.id  # type: ignore
        return False

    def __repr__(self) -> str:
        return pformat(self.serialize())

    @property
    def id(self) -> _PKey:
        """
        Get state model id

        :return: state model id
        :rtype: _PKey
        """
        return self.__id

    @id.setter
    def id(self, _id: _PKey) -> None:
        """
        Set state model id

        :param _id: state model id
        :type _id: _PKey
        """
        self.__id = _id

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, **kwargs) -> None:
        raise NotImplementedError
