
import json, time, threading, uvicorn
from p2pnetwork.node import Node
from pathlib import Path
from fastapi import FastAPI

from source.errors.blockErrors import DuplicateBlockError
import source.events.chainSharing
import source.events.disocver
import source.events.blocks


from source.models.constants import BOOTSTRAP_NODES
from source.models.Models import (Action, Block, Query, NodeMetadata,
                                  NodeConnectionType, DiscoverMessage, ChainSyncRequest,
                                  Payload)
from source.services.verifier import Verifier
from source.utils.logger import Logger
from source.utils.nodeStorageManager import NodeStorageManager
from source.utils.blocks.blockManager import BlockManager
from source.utils.interaction import  NewInteraction
from source.utils.chain.chainSync import ChainSync
from source.services.ledger import Ledger
from source.services.network import Network
from source.models.events import InteractionContext
from source.models.network import NetworkContext

from source.errors import (
    LedgerCorruptError, LedgerNotFoundError
    )



class Peer:
    def __init__(self, title: str, host: str, port: int, bootstrap: bool = False) -> None:
        self.title = title
        self.host = host
        self.port = port
        ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-{self.title}.json"

        if self.host == "localhost": self.host = "127.0.0.1"

        networkContext = NetworkContext(seenBlocks=set(), receivedLengths=[], receivedLedgers=[])

        self.nodeManager = NodeStorageManager(self.title)
        self.ledger = Ledger(ledgerFilePath)
        self.blockManager = BlockManager(self.ledger, networkContext.seenBlocks)
        self.network = Network(self.title, self.host, self.port, self.nodeManager, self.blockManager, self.ledger, networkContext)

        self.me = self.network.metadata
        self.storageManager = self.nodeManager
        self.receivedLedgers: list = []
        self.receivedLengths: list = []
        self.seenBlocks = networkContext.seenBlocks
        self.chainSync = self.network.chainSharing

        if bootstrap == True:
            BOOTSTRAP_NODES.append((self.host, self.port))

        self.startAPI()

    def startNetwork(self) -> None:
        self.network.start()

    def stopNetwork(self) -> None:
        self.network.stop()

    def connect(self, node: NodeMetadata, host: str = "", port: int = 0) -> None:
        self.network.connect(node=node, host=host, port=port)


    def requestChainSync(self) -> None:
        self.ledger.shouldRequestChain = True
        self.receivedLedgers.clear()
        self.chainSync.request()

    
    def startAPI(self) -> None:
            app = self.buildAPI()
            thread = threading.Thread(
                target=uvicorn.run,
                args=(app,),
                kwargs={
                    "host": self.host,
                    "port": self.port + 10000,
                    "log_level": "warning"
                },
                daemon=True
            )

            thread.start()

            # api_port = self.port + 10000


    def buildAPI(self) -> FastAPI:
        from source.API.router import buildRouter
        app = FastAPI(title=f"Peer Node - {self.title}")
        app.include_router(buildRouter(self))
        return app

    

    def registerBlock(self, block: Block) -> Block | None:
        try:
            resultBlock: Block = self.blockManager.registerBlock(block)
        except DuplicateBlockError:

            return None

        if self.blockManager.shouldBoradcast(block):
            self.network.broadcast(Payload(action=Action.BlockBroadcast.value, data=block), [])
            self.seenBlocks.add(block.data.chid)
            return resultBlock


    
        


if __name__ == "__main__":
    from source.models import Authority, User, Identity, CHID

    issuer = Authority(name="JPUF", businessID=3423)

    user1  = User(name="Local", nationalNumber=1111, phone=1, age=30, email="", birth="")
    doc1   = Identity(image="", credentialID=1)
    block1 = Block(data=CHID(user=user1, credential=doc1, issuer=issuer))


    Blockchain = Peer("Blockchain", "localhost", 8000)
    time.sleep(0.1)
    client     = Peer("client",     "localhost", 8282)
    bashar     = Peer("Bashar",     "localhost", 5001)
    bilal      = Peer("Bilal",      "localhost", 5005)
    Ali        = Peer("Ali",        "localhost", 4040)
    Omar       = Peer("Omar",       "localhost", 5011)
    gov        = Peer("GOV",        "localhost", 9999)
    newP       = Peer("new",        "localhost", 8888)
    test       = Peer("Test",       "localhost", 1111)
    np = Peer("NewPeer", "localhost", 2222)

    Blockchain.startNetwork()
    time.sleep(0.3)

    client.startNetwork()       
    bashar.startNetwork()        
    bilal.startNetwork()
    Ali.startNetwork()
    Omar.startNetwork()
    gov.startNetwork()
    newP.startNetwork()
    test.startNetwork()
    np.startNetwork()

    time.sleep(0.5)

    np.registerBlock(block1)


    time.sleep(0.1)

    # Blockchain.stopNetwork()
    # client.stopNetwork()
    # bashar.stopNetwork()
    # bilal.stopNetwork()
    # Ali.stopNetwork()
    # Omar.stopNetwork()
    # gov.stopNetwork()
    # newP.stopNetwork()
    # test.stopNetwork()
    # np.stopNetwork()

