import time
from dataclasses import asdict

from source.models.Models import Authority, Block, CHID, Identity, User, Qwery
from source.services.peer import Peer

if __name__ == "__main__":
    fake_user = User(name="", nationalNumber=0, phone=0, age=0, email="", birth="")

    user = User(name="Testing the block propagation (Client)", nationalNumber=2312311,
                phone=444, age=24, email="", birth="")


    issuer = Authority(name="JPUF", businessID=3423)

    doc = Identity(user=user, issuer=issuer, image="", credentialID=333)

    chid = CHID(user=user, credential=doc, issuer=issuer)

    block = Block(data=chid)


    Blockchain = Peer("Blockchain", "localhost", 8281)
    client = Peer("client", "localhost", 8282)
    bashar = Peer("Bashar", "localhost", 5001)

    Blockchain.start()
    client.start()
    bashar.start()

    time.sleep(0.5)

    bashar.connect_with_node("localhost", 8282)
    bashar.connect_with_node("localhost", 8281)

    Blockchain.connect_with_node("localhost", 8282)
    Blockchain.connect_with_node("localhost", 5001)


    time.sleep(0.5)


    client.registerBlock(block=block)


    print(Blockchain.all_nodes)


    time.sleep(2)

    Blockchain.stop()
    client.stop()
    bashar.stop()
