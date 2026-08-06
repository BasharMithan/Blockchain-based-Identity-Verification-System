import json, time
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from typing import Any

from source.utils.nodeStorageManager import NodeStorageManager
from source.models.Models import (
    Block, Action, Response, DiscoverMessage,
    PeerSyncResponse, NodeMetadata, ChainSyncRequest, ChainSyncResponse,
    Payload, NodeConnectionType
    )

from source.models.events import InteractionContext

from source.models.Models import Query
from source.utils.logger import Logger
from source.utils.blocks.blockManager import BlockManager
from source.services.verifier import Verifier
from source.utils.chain.chainSync import ChainSync

from source.events.eventTools import EventRegiseration

from source.errors import (
    DuplicateBlockError, InvalidBlockPayloadError, InvalidChainError,
    BlockHashMismatchError, BlockNotMinedError, BlockPreviousHashError)


class Interaction:
    def __init__(self, context: InteractionContext) -> None:
        self.context = context
          

    def handle(self, payload: Payload, sender: NodeMetadata) -> None:

        action = payload.action
        data = payload.data



        event = EventRegiseration.resolve(action=str(action), data=data)
        event.excute(self.context, payload=payload, sender=sender) if event else None