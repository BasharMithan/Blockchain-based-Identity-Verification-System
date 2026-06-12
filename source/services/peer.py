
import json
from p2pnetwork.node import Node


from source.models.Models import Action, Block, Qwery, NodeMetadata, NodeConnectionType
from source.services.verifier import Verifier
from source.utils.logger import Logger
from source.utils.nodeStorageManager import NodeStorageManager
from source.services.blockManager import BlockManager

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

    def __init__(self, host, port: int) -> None:
        self.host = host
        self.port = port
        self.discoveredNodes = {}
        self.seenBlocks: set = set()
        Logger.info(f"Initiating a node on {self.host}:{self.port}")
        self.storageManager = NodeStorageManager("main - node")
        self.blockManager = BlockManager()
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
        print(f"[Peer] node_message received from {node}")

        action = data.get("action")

        if action not in Action.getactionsaslist():
            Logger.warning(f"[Peer] Unknown action: got: {action}, available actions: {Action.getactionsaslist()}")
            return
        
        payload   = data.get("data")

        print(f"[Peer] payload action={action} data-type={type(payload)}")
        print(f"Got traffic from: {node}")

        # Registeration Path
        if (action == Action.registeration.value):

            chid = payload["data"]["chid"]  # type: ignore

            if (chid in self.seenBlocks):
                return # Block already processed.

            self.seenBlocks.add(chid) # type: ignore
             
            try:
                block = Block.model_validate(payload)   
                self.blockManager.receiveBlock(block)

                # Block Propagation
                self.send_to_nodes({
                    "action": Action.registeration.value,
                    "data": payload
                }, exclude=[node])



            except InvalidBlockPayloadError as error:
                Logger.warning(f"[Peer] Invalid block payload: {str(error)}")

            except (
                BlockNotMinedError, DuplicateBlockError, BlockPreviousHashError,
                BlockHashMismatchError) as error:
                Logger.warning(f"[Peer] Block validation failed: {str(error)}")


            except InvalidChainError as error:
                Logger.warning(f"[Peer] Chain validation failed: {str(error)}")
                self.stop()



        # Ownership Checking Path
        elif (action == Action.query.value):

            print("Processing a qwery")
            response = Verifier.check(Qwery.model_validate(payload))   
            print(response)

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