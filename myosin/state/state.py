# -*- coding: utf-8 -*-
"""
State Context Manager 
=====================

Copyright © 2022 Christian Sargusingh. All rights reserved.
"""

import copy
import logging
from typing import Dict, Set, Type, Callable, TypeVar

from myosin.state.ssm import SSM
from myosin.typing import AsyncCallback
from myosin.utils.funcs import pformat
from myosin.utils.metrics import Metrics as metrics
from myosin.models.state import StateModel
from myosin.exceptions.state import ModelNotFound, UninitializedStateError

#: generic :class:`myosin.models.state.StateModel` type
GenericModel = TypeVar('GenericModel', bound=StateModel)


class State:
    """
    State access context manager. Read, write or subscribe to registered
    :class:`myosin.models.state.StateModel` objects. Request mutex locks on one or multiple state 
    models by passing the model class in the initializer. If possible avoid nested context manager 
    entry.

    .. code-block:: python

        from myosin import State

        with State(Model) as state:
            model = state.checkout(Model)
            ...
    """

    # shared state memory
    _ssm: Dict[int, SSM] = {}

    def __init__(self, *args: Type[StateModel]) -> None:
        """
        Open a session for state model read and write operations.

        :raises ModelNotFound: if requested state models are not registered.
        """
        self._logger = logging.getLogger(__name__)
        # use set to ensure locking accessors are mutually exclusive
        self.accessors: Set[SSM] = set()
        for arg in args:
            try:
                accessor = self._ssm[hash(arg)]
            except KeyError as exc:
                raise ModelNotFound(
                    f"Could not identify model of type {arg}. Model is not registered.") from exc
            self.accessors.add(accessor)

    def __enter__(self):
        metrics.active_contexts.inc()
        for accessor in self.accessors:
            accessor.lock.acquire()
            self._logger.info("Acquired %s state lock", accessor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for accessor in self.accessors:
            accessor.lock.release()
            self._logger.info("Released %s state lock", accessor)
        metrics.active_contexts.dec()

    def load(self, model: GenericModel) -> GenericModel:
        """
        Register :class:`myosin.models.state.StateModel` into global system state registry. 
        If a model of the same type is found in the system cache, overwrite default properties with
        that of the cached state.

        :param model: user-defined state model. Must implement :class:`myosin.models.state.StateModel`.
        :type model: GenericModel
        :raises UninitializedStateError: if user-defined state model cannot be serialized
        :return: model loaded into state registry
        :rtype: GenericModel 
        """
        # attempt to load a previously cached model into the system state.
        model.load()
        # validate the object is json serializable
        try:
            serialized_model = model.serialize()
        except AttributeError as exc:
            raise UninitializedStateError(
                f"Failed to register model of type {type(model)}. Cannot be serialized.") from exc
        self._ssm[model.__typehash__()] = SSM[GenericModel](model)
        self._logger.info("Loaded state model: %s", pformat(serialized_model))
        return model

    def checkout(self, state_type: Type[GenericModel]) -> GenericModel:
        """
        Return a deepcopy of a registered user-defined state model.

        :param state_type: user-defined registered state model type
        :type state_type: Type[GenericModel]
        :raises ModelNotFound: if the requested state type does not exist
        :return: deep copy of requested state model
        :rtype: GenericModel
        """
        with metrics.checkout_latency.labels(f"{state_type.__qualname__}").time():
            self._logger.info("Checking out state model of type %s", state_type)
            _type_hash = hash(state_type)
            self._logger.debug("Computed type hash: %s", _type_hash)
            ssm = self._ssm.get(_type_hash)
            if not ssm:
                raise ModelNotFound
            _copy = copy.deepcopy(ssm.ref)
        return _copy

    def commit(self, state: StateModel, cache: bool = False) -> None:
        """
        Commit new state to system state and update state subscriber callbacks

        :param state: modified copy of state
        :type state: StateModel
        :param cache: cache the state to disk once updated, defaults to False
        :type cache: bool, optional
        :raises ModelNotFound: if system state has no state registered of the requested type
        """
        with metrics.commit_latency.labels(f"{state.__class__.__qualname__}").time():
            # do not trust any external pass-by-reference objects!
            state = copy.deepcopy(state)
            self._logger.info("Committing state model of type %s with cache mode: %s",
                              type(state), "enabled" if cache else "disabled")
            # automatic type inference by typehash
            _type_hash = state.__typehash__()
            self._logger.debug("Computed type hash: %s", _type_hash)
            # verify typehash exists in ssm registry
            if _type_hash not in self._ssm:
                self._logger.error(
                    "Committed typehash: %s did not match any state model", _type_hash)
                raise ModelNotFound
            ssm = self._ssm[_type_hash]
            ssm.ref = state
            if len(ssm.queue) > 0:
                self._logger.debug("Executing asynchronous callback queue")
                ssm.execute()
            if cache:
                state.cache()
                self._logger.debug("Cached commited state model %s", state)

    def subscribe(self, state_type: Type[GenericModel], callback: Callable[[GenericModel], AsyncCallback]) -> None:
        """
        Subscribe an asynchronous state change listener to a designated runtime model

        :param state_type: model type to subscribe to
        :type state_type: Type[GenericModel]
        :param callback: state change listener callback
        :type callback: Callable[[GenericModel], AsyncCallback]
        """
        _type_hash = hash(state_type)
        ssm = self._ssm.get(_type_hash)
        if not ssm:
            self._logger.error("Subscribed typehash: %s did not match any state model", _type_hash)
            raise ModelNotFound
        ssm.queue.append(callback)

    def reset(self) -> None:
        """
        Reset all loaded state models and clear cached documents
        """
        self._logger.info("Resetting global system state")
        for _, ssm in self._ssm.items():
            ssm.ref.clear()
        self._ssm.clear()
