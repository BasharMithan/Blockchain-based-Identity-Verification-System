
import json, time, threading, uvicorn
from p2pnetwork.node import Node
from pathlib import Path
from fastapi import FastAPI



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

        self.storageManager = NodeStorageManager(self.peerName)

        self.discoveredNodes = {}

        ledgerFilePath = ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-{self.peerName}.json"

        self.ledger = Ledger(ledgerFilePath)

        self.seenBlocks: set = set()
        Logger.info(f"[Interaction - Init] Initiating the node ({self.peerName}) on {self.host}:{self.port}")

        self.blockManager = BlockManager(self.ledger, network=self, seenBlocks=self.seenBlocks)

        super(Peer, self).__init__(self.host, self.port, callback=None)

        self.network = self
        self.me: NodeMetadata = self.myMetaData()

        self.receivedLedgers: list = [] # Needed for the chain sharing class
        self.receivedLengths: list = []

        self.chainSync = ChainSync(
            ledger=self.blockManager.ledger,
            network=self,
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


        self.startAPI()


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
        print(f"[{self.peerName}] API running on {self.host}:{api_port}.")

    def buildAPI(self) -> FastAPI:
        from source.API.router import buildRouter
        app = FastAPI(title=f"Peer Node - {self.peerName}")
        app.include_router(buildRouter(self.blockManager, self.me))
        return app
        


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
