import time
from dataclasses import asdict

from source.models.Models import Authority, Block, CHID, Identity, User, Qwery
from source.services.peer import Peer
from source.services.network import Network




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
    Omar       = Peer("Omar",       "localhost", 5011)
    gov        = Peer("GOV",        "localhost", 9999)
    newP       = Peer("new",        "localhost", 8888)
    test       = Peer("Test",       "localhost", 1111)

    Blockchain.start()   # bootstrap — starts first, waits
    time.sleep(0.3)


    client.start()       
    bashar.start()        
    bilal.start()
    Ali.start()
    Omar.start()
    gov.start()
    newP.start()
    test.start()

    time.sleep(3)        # peer exchange completes


    bashar.registerBlock(block=block1)
    time.sleep(1)

    client.registerBlock(block=block2)
    time.sleep(2)

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
    print(f"    Test: {len(test.all_nodes)}")



    # Now request chain sync — once, cleanly, with full peer list known
    client.requestChainSync()
    bashar.requestChainSync()
    bilal.requestChainSync()
    Ali.requestChainSync()
    Omar.requestChainSync()
    gov.requestChainSync()
    Blockchain.requestChainSync()
    newP.requestChainSync()
    test.requestChainSync()

    time.sleep(2)

    print(f"client received {len(client.receivedLedgers)} ledgers")
    print(f"bashar received {len(bashar.receivedLedgers)} ledgers")
    print(f"Bilal received {len(bilal.receivedLedgers)} ledgers") 
    print(f"Ali received {len(Ali.receivedLedgers)} ledgers") 
    print(f"Omar received {len(Omar.receivedLedgers)} ledgers") 
    print(f"Gov received {len(gov.receivedLedgers)} ledgers") 
    print(f"Test received {len(test.receivedLedgers)} ledgers") 


    # client.startAPI()
    # bashar.startAPI()
    # bilal.startAPI()
    # Omar.startAPI()
    # gov.startAPI()
    # Blockchain.startAPI()
    # newP.startAPI()



    Blockchain.stop()
    client.stop()
    bashar.stop()
    bilal.stop()
    Ali.stop()
    Omar.stop()
    gov.stop()
    newP.stop()
    test.stop()