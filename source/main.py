import time
from dataclasses import asdict

from source.models.Models import Authority, Block, CHID, Identity, User, Qwery
from source.services.peer import Peer


if __name__ == "__main__":
    issuer = Authority(name="JPUF", businessID=3423)

    user1  = User(name="Alice - Bilal", nationalNumber=1111, phone=1, age=30, email="", birth="")
    doc1   = Identity(user=user1, issuer=issuer, image="", credentialID=1)
    block1 = Block(data=CHID(user=user1, credential=doc1, issuer=issuer))

    user2  = User(name="Bob", nationalNumber=2222, phone=2, age=25, email="", birth="")
    doc2   = Identity(user=user2, issuer=issuer, image="", credentialID=2)
    block2 = Block(data=CHID(user=user2, credential=doc2, issuer=issuer))

    Blockchain = Peer("Blockchain", "localhost", 8000)

    client     = Peer("client",     "localhost", 8282)
    bashar     = Peer("Bashar",     "localhost", 5001)
    bilal      = Peer("Bilal",      "localhost", 5005)
    Ali        = Peer("Ali",        "localhost", 4040)

    Blockchain.start()   # bootstrap — starts first, waits
    time.sleep(0.3)


    client.start()       # connects to bootstrap, sends DISCOVER, gets PeerSync
    bashar.start()       # connects to bootstrap, sends DISCOVER, gets PeerSync (including client)
    bilal.start()
    Ali.start()
    time.sleep(1)        # peer exchange completes


    # bashar.registerBlock(block=block1)
    # time.sleep(1)

    # client.registerBlock(block=block2)
    # time.sleep(2)

    print(f"Blockchain: {len(Blockchain.blockManager.ledger.blocks)} blocks")
    print(f"client:     {len(client.blockManager.ledger.blocks)} blocks")
    print(f"bashar:     {len(bashar.blockManager.ledger.blocks)} blocks")
    print(f"Bilal:      {len(bilal.blockManager.ledger.blocks)} blocks")


    print("Connections:")
    print(f"    Blockchain: {len(Blockchain.all_nodes)}")
    print(f"    Bashar: {len(bashar.all_nodes)}")
    print(f"    Client: {len(client.all_nodes)}")
    print(f"    Bilal: {len(bilal.all_nodes)}")
    print(f"    Ali: {len(Ali.all_nodes)}")


    print(Ali.all_nodes)

    Blockchain.stop()
    client.stop()
    bashar.stop()
    bilal.stop()
    Ali.stop()