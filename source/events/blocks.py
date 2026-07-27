from source.events.eventTools import EventRegiseration, Event
from source.models import Action, NodeMetadata, Payload, Block
from source.models.events import InteractionContext

from source.errors import DuplicateBlockError


@EventRegiseration.register
class BlockRegisteractionEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.registeration.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:
        block: Block = Payload.data
        context.blockManager.registerBlock(block=block)

    def broadcastBlock(self, block: Block, context: InteractionContext) -> None:
        if block.data.chid not in context.seenBlocks:

            context.network.send_to_nodes(data={
                "data":block.model_dump(mode="json"),
                "action": Action.BlockBroadcast.value}, exclude=[context.sender]
                )

        

@EventRegiseration.register
class BlockBroadcastEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.BlockBroadcast.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:
        block = Block.model_validate(payload.data)

        try:
            context.blockManager.receiveBlock(block=block)
        except DuplicateBlockError:
            return

