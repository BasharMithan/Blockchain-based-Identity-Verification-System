
import json, time, threading, uvicorn
from p2pnetwork.node import Node
from pathlib import Path
from fastapi import FastAPI

from source.errors.blockErrors import DuplicateBlockError
import source.events.chainSharing
import source.events.disocver
import source.events.blocks


from source.models.constants import BOOTSTRAP_NODES
from source.models.Models import (Action, Block, Qwery, NodeMetadata,
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



class Peer(Node):
    """The class that inherits the `Node` logic and meets the requirements of the projects,
    hence it contains the two primary paths of the project:
    - **Registering a block**: Done the the `registerBlock(block: Block)` function.
    - **Checking identitiy ownership**: Done by the `processQwery(qwery: Qwery)` function."""

    def __init__(self, name: str, host, port: int) -> None:
        self.peerName = name
        self.host = host
        self.port = port


        if self.host == "localhost": self.host = "127.0.0.1"

        self.network = self

        self.storageManager = NodeStorageManager(self.peerName)

        self.discoveredNodes = {}

        ledgerFilePath = ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-{self.peerName}.json"

        self.ledger = Ledger(ledgerFilePath)

        self.seenBlocks: set = set()
        Logger.info(f"[Interaction - Init] Initiating the node ({self.peerName}) on {self.host}:{self.port}")

        self.blockManager = BlockManager(self.ledger, seenBlocks=self.seenBlocks)

        super(Peer, self).__init__(self.host, self.port, callback=None)

        self.me: NodeMetadata = self.myMetaData()

        self.receivedLedgers: list = [] # Needed for the chain sharing class
        self.receivedLengths: list = []

        self.chainSync = ChainSync(
            ledger=self.blockManager.ledger,
            network=self.network,
            receivedLedgers=self.receivedLedgers,
            receivedLengths=self.receivedLengths,
            me=self.me)

        """
        self.interaction = Interaction(
            me=self.me,
            network=self,
            blockManager=self.blockManager,
            nodeManager=self.storageManager,
            seenBlocks=self.seenBlocks,
            connections=self.storageManager.nodes,
            receivedLedgers=self.receivedLedgers,
            receivedLengths=self.receivedLengths,
            chainSync=self.chainSync
            )"""




    def myMetaData(self) -> NodeMetadata:
        return NodeMetadata(
            name=self.peerName,
            nodeID=self.id,
            host=self.host,
            port=int(self.port),
            connectionType=NodeConnectionType.outbound
        )


    def start(self):
        super().start()
        time.sleep(0.1)   
        self.__connectToBootstrap()


    
    def requestChainSync(self) -> None:
        """
        Sends a single ChainSyncRequest to all currently connected peers.
        Clears receivedLedgers first so previous sessions don't pollute the result.
        """

        self.receivedLedgers.clear()
        self.chainSync.request()


    def __connectToBootstrap(self) -> None:
        for host, port in BOOTSTRAP_NODES:
            if host == self.host and port == self.port:
                continue
            Logger.info(f"[Peer] Connecting to bootstrap {host}:{port}")
            self.connect_with_node(host, port)


    def processQwery(self, qwery: Qwery) -> None:
        """**Path 1 (Ownership checking):** The entry point to processing a qwery."""

        payload =  {
            "action": Action.query.value, 
            "data": qwery.model_dump()
            }
        
        self.send_to_nodes(payload)


    def registerBlock(self, block: Block) -> None:
        """**Path 2 (Block registeration):** Acts as an entry point
        to the user, when adding a new block to the network."""

        try:
            fullBlock = self.blockManager.registerBlock(block)
        
            blockAsDict = Block.model_dump_json(fullBlock) 


            self.send_to_nodes({
                "action": Action.registeration.value,
                "data": json.loads(blockAsDict) 
                 })

        except (LedgerCorruptError, LedgerNotFoundError) as error:
            Logger.warning(f"[Peer] Fatal ledger error: {error}")
            self.stop()   # ledger is unreadable — stopping is justified

        except Exception as error:
            Logger.warning(f"[Peer] Unable to register block: {error}")
            

    def node_message(self, node, data: dict):
        "TODO: Solve the block broadcast issue."

        context = InteractionContext(
            network=self,
            blockManager=self.blockManager,
            chainSync=self.chainSync,
            nodeManager=self.storageManager,
            seenBlocks=self.seenBlocks,
            receivedLedgers=self.receivedLedgers,
            receivedLengths=self.receivedLengths,
            me=self.myMetaData(),
            connections=self.all_nodes,
            sender=node
            )

        sender = NodeStorageManager.nodeConnectionToMetadata(connectionType=NodeConnectionType.outbound, nodeConnection=node)

        payload = Payload.model_validate(data)

        newInteraction = NewInteraction(context=context)

        newInteraction.handle(payload=payload, sender=sender)
        

        # block = self.interaction.getAsBlock(interaction=data)
        
        # if self.interaction.shouldBroadcast(block):
        #     block = self.interaction.getAsBlock(interaction=data)
        #     if block:
        #         self.broadcast_block(node, block)

        # self.interaction.handle(data)
    


    def broadcast_block(self, node, block: Block) -> None:
        """Broadcast a validated block to connected peers."""
        self.send_to_nodes({
            "action": Action.BlockBroadcast.value,
            "data": Block.model_dump(block),
            "sender": self.peerName
        }, exclude=[node])

        Logger.info(f"[Block Broadcast] Broadcasting the block: '{block.data.user.name}'...")


        
    def __Discover(self, toAll: bool) -> None:

        message: DiscoverMessage = DiscoverMessage(
            sender=self.me,
            toAll=toAll
        )

        self.send_to_nodes(
            {
                "action": Action.discover.value,
                "data": message.model_dump(mode="json")
            }
        )

        Logger.info(f"[Peer ({self.peerName}) - Discover] Sending the discovery message.")

    

    def inbound_node_connected(self, node):

        # Checking if the node is in the Bootstrap list
        if (self.host, self.port) in BOOTSTRAP_NODES:
            Logger.info(f"[Peer - Bootstrap]  Got a connection from: {node.host}:{node.port}") 

        # self.storageManager.registerNode(
        #     node=NodeMetadata(name=self.peerName, nodeID=node.id, host=node.host, port=int(node.port), connectionType=NodeConnectionType.inbound)
        #     )

        self.storageManager.update(self.nodes_inbound, NodeConnectionType.inbound)
        
        return super().inbound_node_connected(node)

    
    def outbound_node_connected(self, node):
        if (node.host, node.port) in BOOTSTRAP_NODES:
            Logger.info(f"[Peer ({self.peerName})] Connected to Bootstrap node {node.host}:{node.port}")
        else: Logger.info(f"[Peer ({self.peerName})] Connected to the node ({node.host}:{node.port}).")

        self.storageManager.update(self.nodes_outbound, NodeConnectionType.outbound)

        # Send DISCOVER when we initiate a connection
        self.__Discover(toAll=True)


        # self.storageManager.registerNode(
        #     node=NodeMetadata(name=self.peerName, nodeID=node.id, host=node.host, port=int(node.port), connectionType=NodeConnectionType.outbound)
        #     )

        return super().outbound_node_connected(node)

    
    def inbound_node_disconnected(self, node):
        return super().inbound_node_disconnected(node)
    
    def outbound_node_disconnected(self, node):
        return super().outbound_node_disconnected(node)


class NewPeer:
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

            api_port = self.port + 10000


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
    doc1   = Identity(user=user1, issuer=issuer, image="", credentialID=1)
    block1 = Block(data=CHID(user=user1, credential=doc1, issuer=issuer))


    Blockchain = NewPeer("Blockchain", "localhost", 8000)
    time.sleep(0.1)
    client     = NewPeer("client",     "localhost", 8282)
    bashar     = NewPeer("Bashar",     "localhost", 5001)
    bilal      = NewPeer("Bilal",      "localhost", 5005)
    Ali        = NewPeer("Ali",        "localhost", 4040)
    Omar       = NewPeer("Omar",       "localhost", 5011)
    gov        = NewPeer("GOV",        "localhost", 9999)
    newP       = NewPeer("new",        "localhost", 8888)
    test       = NewPeer("Test",       "localhost", 1111)
    np = NewPeer("NewPeer", "localhost", 2222)

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

    time.sleep(0.3)

    np.registerBlock(block1)


    time.sleep(0.1)

    Blockchain.stopNetwork()
    client.stopNetwork()
    bashar.stopNetwork()
    bilal.stopNetwork()
    Ali.stopNetwork()
    Omar.stopNetwork()
    gov.stopNetwork()
    newP.stopNetwork()
    test.stopNetwork()
    np.stopNetwork()

