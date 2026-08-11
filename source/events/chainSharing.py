from events.eventTools import Event, EventRegiseration
from models.Models import Action, NodeMetadata, Payload, ChainSyncRequest, ChainSyncResponse
from models.events import InteractionContext


@EventRegiseration.register
class ChainSyncRequestEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.chainSyncRequest.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:

        request = ChainSyncRequest.model_validate(payload.data)

        context.chainSync.send(request=request)



@EventRegiseration.register
class ChainSyncResponseEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.chainSyncResponse.value


    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:

        response = ChainSyncResponse.model_validate(payload.data)

        context.chainSync.receive(response=response)