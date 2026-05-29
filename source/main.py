import time
import pprint
from dataclasses import asdict

from source.models.Models import Action, Authority, Block, CHID, Identity, User, Qwery
from source.services.BlockchainNetwork import BlockchainNetworkHandler

if __name__ == "__main__":
    fake_user = User(name="", nationalNumber=0, phone=0, age=0, email="", birth="")

    user = User(name="Testing the Block Registeration - 2", nationalNumber=2312311,
                phone=444, age=24, email="", birth="")


    issuer = Authority(name="JPU", businessID=3423)

    doc = Identity(user=user, issuer=issuer, image="", credentialID=333)

    chid = CHID(user=user, credential=doc, issuer=issuer)

    block = Block(index=0, data=chid)


    Blockchain = BlockchainNetworkHandler("localhost", 8281)
    client = BlockchainNetworkHandler("localhost", 8282)

    Blockchain.start()
    client.start()

    time.sleep(0.5)

    client.connect_with_node("localhost", 8281)

    time.sleep(0.5)


    # client.registerBlock(block=block)

    ownershipQwery = Qwery(user=user, credential=doc)

    client.processQwery(ownershipQwery)



    time.sleep(2)

    Blockchain.stop()
    client.stop()