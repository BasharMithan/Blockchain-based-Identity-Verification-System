from p2pnetwork.node import Node

from source.models.Models import Block, User, Authority, Identity, CHID, Response
from source.utils.ledger import Ledger

class BlockchainNetworkHandler(Node):
    def __init__(self, host, port: int) -> None:
        super(BlockchainNetworkHandler, self).__init__(host, port, None)
        self.ledgerHandler: Ledger = Ledger()
        self.blocks: list[Block] = self.ledgerHandler.blocks

    def __registerBlock(self, block: Block) -> None:
        ...

    def __searchLedger(self, CHID: str) -> Block | None:
       ...

    def registerBlock(self, user: User, identity: Identity, authority: Authority) -> bool:
        ...

    def DSCOwnershipCheck(self, node, data: dict) -> Response:
        ...

bs = BlockchainNetworkHandler("localhost", 8281)

class __Verifier:
    def __int__(self) -> None:
        pass

    def DECOwnershipCheck(self, credentialID: str, userID: str) -> bool:
        ...
        


user = User("bashar", 1192939293, 999, 24, "b@m.c", "")
issuer = Authority("GOV", 3424234)
identity = Identity(user, issuer, "", 343454564)

bs.registerBlock(user=user, identity=identity, authority=issuer)

print(bs.all_nodes)
   