
import logging
from copy import deepcopy
from dataclasses import asdict
from p2pnetwork.node import Node


from source.models.Models import Action, Block, Qwery, Response
from source.services.ledger import Ledger
from source.services.verifier import Verifier



class BlockchainNetworkHandler(Node):
    def __init__(self, host, port: int) -> None:
        self.host, self.port = host, port
        super(BlockchainNetworkHandler, self).__init__(self.host, self.port, callback=None)
        self.ledgerHandler: Ledger = Ledger()
        self.blocks: list[Block] = self.ledgerHandler.blocks
        


    def processQwery(self, qwery: Qwery) -> None:
        payload =  {
            "action": Action.query.value, 
            "data": Qwery.model_dump_json(qwery)
            }
        

        self.send_to_nodes(payload)


    def registerBlock(self, block: Block) -> None:
        self.send_to_nodes({
            "action": Action.registeration.value,
            "data": Block.model_dump(block)
             })


    def node_message(self, connected_node, payload: dict): # pyright: ignore[reportIncompatibleMethodOverride]
        action = payload.get("action")
        data   = payload.get("data")

        print(f"Got traffic from: {connected_node}")

        if (action == Action.registeration.value):

            print("Registering a block")
            self.ledgerHandler.insertBlock(data) # type: ignore

        elif (action == Action.query.value):

            print("Processing a qwery")
            response = Verifier.check(Qwery.model_validate_json(data)) # type: ignore
            print(response)


