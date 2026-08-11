import json, time
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from typing import Any

from utils.nodeStorageManager import NodeStorageManager
from models.Models import (
    Block, Action, Response, DiscoverMessage,
    PeerSyncResponse, NodeMetadata, ChainSyncRequest, ChainSyncResponse,
    Payload, NodeConnectionType
    )

from models.events import InteractionContext

from models.Models import Query
from utils.logger import Logger
from utils.blocks.blockManager import BlockManager
from services.verifier import Verifier
from utils.chain.chainSync import ChainSync

from events.eventTools import EventRegiseration

from errors import (
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