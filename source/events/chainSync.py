from source.events.eventTools import Event, EventRegiseration
from source.models.Models import Action


@EventRegiseration.register
class ChainSyncRequestEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.chainSyncRequest.value


    def excute(self, context, payload, sender) -> None:
        print(f"Event {self.eventAction()} is ready to be excuted.")


@EventRegiseration.register
class ChainSyncResponseEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.chainSyncResponse.value

    def excute(self, context, payload, sender) -> None:
        print(f"Event {self.eventAction()} is ready to be excuted.")