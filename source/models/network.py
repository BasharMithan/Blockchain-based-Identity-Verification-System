from dataclasses import dataclass

from models import NodeMetadata
from utils.nodeStorageManager import NodeStorageManager 
from utils.blocks.blockManager import BlockManager

@dataclass
class NetworkContext:
    receivedLengths: list
    receivedLedgers: list
    seenBlocks: set
