
from p2pnetwork.node import Node

from source.models.Models import Action, Block, Qwery, NodeMetadata, NodeConnectionType
from source.services.verifier import Verifier
from source.utils.logger import Logger
from source.utils.nodeStorageManager import NodeStorageManager
from source.services.blockManager import BlockManager



class Peer(Node):
    """The class that inherits the `Node` logic and meets the requirements of the projects,
    hence it contains the two primary paths of the project:
    - **Registering a block**: Done the the `registerBlock(block: Block)` function.
    - **Checking identitiy ownership**: Done by the `processQwery(qwery: Qwery)` function."""

    def __init__(self, host, port: int) -> None:
        self.host, self.port = host, port
        self.discoveredNodes = {}

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

        self.send_to_nodes({
            "action": Action.registeration.value,
            "data": block.model_dump()
             })


    def node_message(self, connected_node, payload: dict): # pyright: ignore[reportIncompatibleMethodOverride]
        action = payload.get("action")
        data   = payload.get("data")

        print(f"Got traffic from: {connected_node}")

        # Registeration Path
        if (action == Action.registeration.value):
            block = Block.model_validate(data)  # type: ignore
            self.blockManager.registerBlock(block)

        # Ownership Checking Path
        elif (action == Action.query.value):

            print("Processing a qwery")
            response = Verifier.check(Qwery.model_validate(data))  # type: ignore
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