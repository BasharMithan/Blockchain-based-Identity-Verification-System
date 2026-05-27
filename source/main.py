from source.models.Models import CHID, User, Authority, Identity, Block
from source.utils.ledger import Ledger
from source.services.BlockchainNetwork import BlockchainNetworkHandler

import time

if __name__ == "__main__":
    user = User("Bashar", 2312311, 444, 24, "", "")
    issuer = Authority("JPU", 3423)
    doc = Identity(user, issuer, "", 333)
    chid = CHID(user=user, credential=doc, issuer=issuer)
    block = Block(0, chid)


    Blockchain = BlockchainNetworkHandler("localhost", 8281)
    client = BlockchainNetworkHandler("localhost", 8282)

    Blockchain.start()
    client.start()

    time.sleep(0.5)

    client.connect_with_node("localhost", 8281)

    time.sleep(0.5)

    client.registerBlock(block)

    time.sleep(2)

    Blockchain.stop()
    client.stop()