
from p2pnetwork.node import Node
from dataclasses import asdict
import pprint

from source.models.Models import Block, Response, Action, Response, Payload
from source.utils.ledger import Ledger

class BlockchainNetworkHandler(Node):
    def __init__(self, host, port: int) -> None:
        self.host, self.port = host, port
        super(BlockchainNetworkHandler, self).__init__(self.host, self.port, callback=None)
        self.ledgerHandler: Ledger = Ledger()
        self.blocks: list[Block] = self.ledgerHandler.blocks
        # self.connect_with_node(self.host, self.port)

    def registerBlock(self, block: Block) -> None:
        self.ledgerHandler.insertBlock(block)
        payload = asdict(Payload(action=Action.registeration.value,
                          block=asdict(block)))
        

        self.send_to_nodes(payload)

    def node_message(self, connected_node, data): # pyright: ignore[reportIncompatibleMethodOverride]
        print(f"Traffic detected! Received data from: {data}")
        
        # You just sort the traffic based on your protocol keys
        if data.get("action") == "NEW_BLOCK":
            print("Successfully processed a new block entry automatically.")
    
    def DSCOwnershipCheck(self, node, data: dict) -> Response:
        ...





class __Verifier:
    def __int__(self) -> None:
        pass

    def DECOwnershipCheck(self, credentialID: str, userID: str) -> bool:
        ...
        

