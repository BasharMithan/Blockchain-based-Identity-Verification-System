# source/events/blocks.py
from events.eventTools import EventRegiseration, Event
from models import Action, NodeMetadata, Payload, Block
from models.events import InteractionContext

from errors import DuplicateBlockError


@EventRegiseration.register
class BlockRegisteractionEvent(Event):

    @classmethod
    def eventAction(cls) -> str:
        return Action.registeration.value

    def excute(self, context: InteractionContext, payload: Payload, sender: NodeMetadata) -> None:
        block: Block = Block.model_validate(payload.data)
        context.blockManager.registerBlock(block=block)
        self.broadcastBlock(block, context)

    def broadcastBlock(self, block: Block, context: InteractionContext) -> None:
        if block.data.chid not in context.seenBlocks:
            context.seenBlocks.add(block.data.chid)
            context.network.send_to_nodes(data={
                "data": block.model_dump(mode="json"),
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

        self.relayBlock(block, context, sender)

    def relayBlock(self, block: Block, context: InteractionContext, sender: NodeMetadata) -> None:
        """Re-broadcasts a received block to this node's own peers, excluding
        whoever just sent it — this is what lets a block propagate past a
        single hop in a non-fully-connected topology."""
        if block.data.chid in context.seenBlocks:
            return
        context.seenBlocks.add(block.data.chid)

        context.network.send_to_nodes(data={
            "data": block.model_dump(mode="json"),
            "action": Action.BlockBroadcast.value}, exclude=[sender]
            )