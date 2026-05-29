
import logging
from copy import deepcopy
from dataclasses import asdict
from p2pnetwork.node import Node


from source.models.Models import Action, Block, Qwery, Response
from source.services.ledger import Ledger
from source.services.verifier import Verifier


qwery_copy: Qwery | None = None
block_copy: Block | None = None
action: str


class BlockchainNetworkHandler(Node):
    def __init__(self, host, port: int) -> None:
        self.host, self.port = host, port
        super(BlockchainNetworkHandler, self).__init__(self.host, self.port, callback=None)
        self.ledgerHandler: Ledger = Ledger()
        self.blocks: list[Block] = self.ledgerHandler.blocks
        # self.connect_with_node(self.host, self.port)


    def processQwery(self, qwery: Qwery) -> None:
        global qwery_copy
        global action

        action = Action.query.value

        qwery_copy = deepcopy(qwery)
        self.send_to_nodes(asdict(qwery))

    def registerBlock(self, block: Block) -> None:
        global action
        global block_copy

        action = Action.registeration.value

        block_copy = deepcopy(block)
        self.send_to_nodes(asdict(block))
        ...


    def node_message(self, connected_node, data: dict): # pyright: ignore[reportIncompatibleMethodOverride]
        global block_copy
        global qwery_copy
        global action

        if (action == Action.registeration.value):
            if (block_copy is None): return

            print("Registering a block")
            self.ledgerHandler.insertBlock(asdict(block_copy)) # type: ignore

        elif (action == Action.query.value):
            if (qwery_copy is None): return

            print("Processing a qwery")
            response = Verifier.check(qwery_copy)
            print(response)


