
import json
from p2pnetwork.node import Node
from pathlib import Path


from source.models.Models import Action, Block, Qwery, NodeMetadata, NodeConnectionType
from source.services.verifier import Verifier
from source.utils.logger import Logger
from source.utils.nodeStorageManager import NodeStorageManager
from source.services.blockManager import BlockManager
from source.utils.interaction import HandleIncomingInteraction

from source.errors import (
    LedgerCorruptError, LedgerNotFoundError, InvalidBlockPayloadError,
    BlockHashMismatchError, BlockNotMinedError,
    DuplicateBlockError, BlockPreviousHashError,
    InvalidChainError)



class Peer(Node):
    """The class that inherits the `Node` logic and meets the requirements of the projects,
    hence it contains the two primary paths of the project:
    - **Registering a block**: Done the the `registerBlock(block: Block)` function.
    - **Checking identitiy ownership**: Done by the `processQwery(qwery: Qwery)` function."""

    def __init__(self, name: str, host, port: int) -> None:
        self.peerName = name
        self.host = host
        self.port = port
        self.discoveredNodes = {}

        ledgerFilePath = ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-{self.peerName}.json"

        self.seenBlocks: set = set()
        Logger.info(f"Initiating a node on {self.host}:{self.port}")
        self.storageManager = NodeStorageManager(f"{self.host}_{self.port}")
        self.blockManager = BlockManager(filePath=ledgerFilePath)
        super(Peer, self).__init__(self.host, self.port, callback=None)


    def processQwery(self, qwery: Qwery) -> None:
        """**Path 1 (Ownership checking):** The entry point to processing a qwery."""

        payload =  {
            "action": Action.query.value, 
            "data": qwery.model_dump()
            }
        
        self.send_to_nodes(payload)


    def registerBlock(self, block: Block) -> None:
        """**Path 2 (Block registeration):** Acts as an entry point
        to the user, when adding a new block to the network."""

        print(f"[Peer] registerBlock broadcast called for block index={block.index}")
        try:
            fullBlock = self.blockManager.registerBlock(block)
        
            blockAsDict = Block.model_dump_json(fullBlock) 

            print(f"[{self.peerName}] Block : {type(json.loads(blockAsDict))}")

            self.send_to_nodes({
                "action": Action.registeration.value,
                "data": json.loads(blockAsDict) 
                 })

        except (LedgerCorruptError, LedgerNotFoundError) as error:
            Logger.warning(f"[Peer] Fatal ledger error: {error}")
            self.stop()   # ledger is unreadable — stopping is justified

        except Exception as error:
            Logger.warning(f"[Peer] Unable to register block: {error}")
            

    def node_message(self, node, data: dict):
        interaction = HandleIncomingInteraction(data, self.blockManager, self.seenBlocks)

        if not interaction.shouldBroadcast():
            return
        else:
            block = interaction.getAsBlock()
            if block:
                interaction.handle()
                self.broadcast_block(node, block)


    def broadcast_block(self, node, block: Block) -> None:
        """Broadcast a validated block to connected peers."""
        self.send_to_nodes({
            "action": Action.BlockBroadcast.value,
            "data": Block.model_dump(block),
            "sender": self.peerName
        }, exclude=[node])

        Logger.info(f"[Block Broadcast] Broadcasting the block: '{block.data.user.name}'...")


    

    def inbound_node_connected(self, node):
        Logger.info(f"Got a connection from: {node.id}") 
        self.storageManager.registerNode(
            node=NodeMetadata(nodeID=node.id, host=node.host, port=int(node.port), connectionType=NodeConnectionType.inbound)
            )
        
        return super().inbound_node_connected(node)
    
    def outbound_node_connected(self, node):
        Logger.info(f"Connected to node: {node.id}")
        self.storageManager.registerNode(
            node=NodeMetadata(nodeID=node.id, host=node.host, port=int(node.port), connectionType=NodeConnectionType.outbound)
            )

        return super().outbound_node_connected(node)

    
    def inbound_node_disconnected(self, node):
        return super().inbound_node_disconnected(node)
    
    def outbound_node_disconnected(self, node):
        return super().outbound_node_disconnected(node)


if __name__ == "__main__":
    pass