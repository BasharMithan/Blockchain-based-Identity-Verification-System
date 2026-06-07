import time
from dataclasses import asdict

from source.models.Models import Authority, Block, CHID, Identity, User, Qwery
from source.services.peer import Peer

if __name__ == "__main__":
    fake_user = User(name="", nationalNumber=0, phone=0, age=0, email="", birth="")

    user = User(name="Testing the Chain Validation - 14", nationalNumber=2312311,
                phone=444, age=24, email="", birth="")


    issuer = Authority(name="JPUF", businessID=3423)

    doc = Identity(user=user, issuer=issuer, image="", credentialID=333)

    chid = CHID(user=user, credential=doc, issuer=issuer)

    block = Block(data=chid)


    Blockchain = Peer("localhost", 8281)
    client = Peer("localhost", 8282)

    Blockchain.start()
    client.start()

    time.sleep(0.5)

    client.connect_with_node("localhost", 8281)

    time.sleep(0.5)


    client.registerBlock(block=block)
    

    ownershipQwery = Qwery(user=user, credential=doc)

    # client.processQwery(ownershipQwery)


    # print(Blockchain.storageManager.nodes)

    time.sleep(2)

    Blockchain.stop()
    client.stop()
