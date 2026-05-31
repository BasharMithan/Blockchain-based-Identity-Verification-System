
from p2pnetwork.node import Node

from source.models.Models import Action, Block, Qwery, Response
from source.services.ledger import Ledger
from source.services.verifier import Verifier
from source.utils.logger import Logger



class BlockchainNetworkHandler(Node):
    """The class that inherits the `Node` logic and meets the requirements of the projects,
    hence it contains the two primary paths of the project:
    - **Registering a block**: Done the the `registerBlock(block: Block)` function.
    - **Checking identitiy ownership**: Done by the `processQwery(qwery: Qwery)` function."""

    def __init__(self, host, port: int) -> None:
        self.host, self.port = host, port
        self.discoveredNodes = {}

        Logger.info(f"Initiating a node on {self.host}:{self.port}")

        # Had to import the ledger to insert blocks
        self.ledgerHandler: Ledger = Ledger()
        
        super(BlockchainNetworkHandler, self).__init__(self.host, self.port, callback=None)


    def processQwery(self, qwery: Qwery) -> None:
        """**Path 1 (Ownership checking):** The entry point to processing a qwery."""

        payload =  {
            "action": Action.query.value, 
            "data": Qwery.model_dump_json(qwery)
            }
        

        self.send_to_nodes(payload)


    def registerBlock(self, block: Block) -> None:
        """**Path 2 (Block registeration):** Acts as an entry point
        to the user, when adding a new block to the network."""

        self.send_to_nodes({
            "action": Action.registeration.value,
            "data": Block.model_dump(block)
             })


    def node_message(self, connected_node, payload: dict): # pyright: ignore[reportIncompatibleMethodOverride]
        action = payload.get("action")
        data   = payload.get("data")

        print(f"Got traffic from: {connected_node}")

        # Registeration Path
        if (action == Action.registeration.value):

            print("Registering a block")
            self.ledgerHandler.insertBlock(data) 

        # Ownership Checking Path
        elif (action == Action.query.value):

            print("Processing a qwery")
            response = Verifier.check(Qwery.model_validate_json(data))  # type: ignore
            print(response)

    def inbound_node_connected(self, node):
        Logger.info(f"Got a connection from: {node.id}") 
        return super().inbound_node_connected(node)
    
    def outbound_node_connected(self, node):
        Logger.info(f"Connected to node: {node.id}")
        return super().outbound_node_connected(node)
    
    def inbound_node_disconnected(self, node):
        return super().inbound_node_disconnected(node)
    
    def outbound_node_disconnected(self, node):
        return super().outbound_node_disconnected(node)


