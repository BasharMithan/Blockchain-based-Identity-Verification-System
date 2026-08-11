from pydantic import BaseModel
from dataclasses import dataclass
from p2pnetwork.nodeconnection import NodeConnection
from p2pnetwork.node import Node

from utils.blocks.blockManager import BlockManager
from utils.chain.chainSync import ChainSync
from utils.nodeStorageManager import NodeStorageManager
from models.Models import NodeMetadata



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