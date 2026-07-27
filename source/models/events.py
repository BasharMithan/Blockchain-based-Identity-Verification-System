from pydantic import BaseModel
from dataclasses import dataclass
from p2pnetwork.nodeconnection import NodeConnection
from p2pnetwork.node import Node

from source.utils.blocks.blockManager import BlockManager
from source.utils.chain.chainSync import ChainSync
from source.utils.nodeStorageManager import NodeStorageManager
from source.models.Models import NodeMetadata



@dataclass
class InteractionContext:
    network: Node
    blockManager: BlockManager
    chainSync: ChainSync
    nodeManager: NodeStorageManager
    seenBlocks: set
    receivedLedgers: list
    receivedLengths: list
    me: NodeMetadata
    connections: list[NodeConnection]
    sender: NodeMetadata


@dataclass
class InteractionRequirements:
    receivedLedgers: list
    receivedLengths: list