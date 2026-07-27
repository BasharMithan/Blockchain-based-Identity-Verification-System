from dataclasses import dataclass

from source.models import NodeMetadata
from source.utils.nodeStorageManager import NodeStorageManager 
from source.utils.blocks.blockManager import BlockManager

@dataclass
class NetworkContext:
    receivedLengths: list
    receivedLedgers: list
    seenBlocks: set
