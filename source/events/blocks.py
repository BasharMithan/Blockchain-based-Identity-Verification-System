from source.events.eventTools import EventRegiseration, Event
from source.models import Action, NodeMetadata, Payload, Block
from source.models.events import InteractionContext

from source.errors import DuplicateBlockError



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
            print("Block Already.")

  
    def shouldBroadcast(self, block: Block, context: InteractionContext) -> bool:
        if block.data.chid in context.seenBlocks:
            return False

        else:
            context.seenBlocks.add(block.data.chid)
            return True
        

    def broadcastBlock(self, block: Block, context: InteractionContext) -> None:

        payload = {
            "action": Action.BlockBroadcast.value,
            "data": block.model_dump(mode="json")
        }

        context.network.send_to_nodes(payload)
