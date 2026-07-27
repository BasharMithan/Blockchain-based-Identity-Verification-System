from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type

from source.models.events import InteractionContext
from source.models.Models import Payload, NodeMetadata


class Event(BaseModel, ABC):
    "A command patten design to reduce code repitition and ease the implementation of new request/response events."

    @classmethod
    @abstractmethod
    def eventAction(cls) -> str:
        "The action enum this event amps to."
        ...

    @abstractmethod
    def excute(cls, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:
        "Contains the handling logic for this action."
        ...


    

class EventRegiseration:
    """Maps action enums to event classes.
    Every event command register itself here at import time."""


    record: dict[str, Type[Event]] = {}

    @classmethod
    def register(cls, event: Type[Event]) -> Type[Event]:
        "Registers an event by its action."

        cls.record[event.eventAction()] = event

        return event


    @classmethod
    def resolve(cls, action: str, data: dict) -> Event | None:
        """Given an action string an raw data dict,
        returns the correct event instance or None if the action is unrecognised."""


        eventClass = cls.record.get(action)

        if eventClass is None:
            return None

        return eventClass.model_validate(data)
