import time
import pprint
from dataclasses import asdict

from source.models.Models import Action, Authority, Block, CHID, Identity, User, Qwery
from source.services.BlockchainNetwork import BlockchainNetworkHandler

if __name__ == "__main__":
    fake_user = User("", 0, 0, 0, "", "")

    user = User("Testing the Block Registeration - 2", 2312311, 444, 24, "", "")
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



    ownershipQwery = Qwery(fake_user, doc)

    client.processQwery(ownershipQwery)

    # client.registerBlock(block=block)


    time.sleep(2)

    Blockchain.stop()
    client.stop()