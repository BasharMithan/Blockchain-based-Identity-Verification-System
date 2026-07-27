import json, time
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from typing import Any

from source.utils.nodeStorageManager import NodeStorageManager
from source.models.Models import (
    Block, Action, Response, DiscoverMessage,
    PeerSyncResponse, NodeMetadata, ChainSyncRequest, ChainSyncResponse,
    Payload, NodeConnectionType
    )

from source.models.events import InteractionContext

from source.models.Models import Qwery as Query
from source.utils.logger import Logger
from source.utils.blocks.blockManager import BlockManager
from source.services.verifier import Verifier
from source.utils.chain.chainSync import ChainSync

from source.events.eventTools import EventRegiseration

from source.errors import (
    DuplicateBlockError, InvalidBlockPayloadError, InvalidChainError,
    BlockHashMismatchError, BlockNotMinedError, BlockPreviousHashError)


class NewInteraction:
    def __init__(self, context: InteractionContext) -> None:
        self.context = context
          

    def handle(self, payload: Payload, sender: NodeMetadata) -> None:

        action = payload.action
        data = payload.data



        event = EventRegiseration.resolve(action=str(action), data=data)
        event.excute(self.context, payload=payload, sender=sender) if event else None
            

# Old Interaction class.
class Interaction:
    def __init__(self, me: NodeMetadata, network: Node,
                 blockManager: BlockManager, nodeManager: NodeStorageManager, seenBlocks: set,
                 connections: list[NodeMetadata], receivedLedgers: list, receivedLengths: list,
                 chainSync: ChainSync) -> None:
        
        self.blockManager = blockManager
        self.nodeManager: NodeStorageManager = nodeManager
        self.me = me
        self.connections: list = connections
        self.seenBlocks: set = seenBlocks
        self.network = network
        self.chainSharing = chainSync




    def getAsBlock(self, interaction: dict) -> Block | None:
        if self.extractAction(interaction=interaction) in (Action.registeration.value, Action.BlockBroadcast.value):
            blockDict = interaction.get("data")
            if isinstance(blockDict, str):
                try:
                    blockDict = json.loads(blockDict)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(blockDict)
        return None
        

    def extractAction(self, interaction: dict) -> str:
         return interaction.get("action") # type: ignore
         
    
    def shouldBroadcast(self, possibleBlock) -> bool:

        if isinstance(possibleBlock, Block):

            if (possibleBlock.data.chid in self.seenBlocks):
                Logger.info(f"[Interaction] Block {possibleBlock.data.user.name} should not be broadcasted.")
                return False

            else:
                Logger.info(f"[Interaction] Block {possibleBlock.data.user.name} should be broadcasted.")
                self.seenBlocks.add(possibleBlock.data.chid)
                return True 
        else: return False
            

    def handle(self, interaction: dict) -> None:
        """Handles the incoming interaction detected in the `node_message` function"""

        Logger.info(f"[Interaction - {self.me.name}] Got an interaction: {interaction.get('action')}.") # type: ignore

        Logger.info(f"[Interaction] Starting the interaction handler.")

        decision = self.__classifyInteraction(interaction=interaction)


        if (isinstance(decision, Block)):

            self.__handleBlockInteraction(decision)

        elif (isinstance(decision, Query)):
            self.__handleQueryInteraction(decision) 

        elif (isinstance(decision, DiscoverMessage)):
            self.__handleDiscoverMessage(decision)

        elif (isinstance(decision, PeerSyncResponse)):
            self.__handlePeerSync(decision)

        elif (isinstance(decision, ChainSyncRequest)):
            self.__handleChainSyncRequest(decision)

        elif (isinstance(decision, ChainSyncResponse)):
            self.__handleChainSyncResponse(decision)




    def __handleBlockInteraction(self, block: Block) -> None:
        """Handles the received block"""


        try:
                self.blockManager.receiveBlock(block)

        except InvalidBlockPayloadError as error:
                Logger.warning(f"[Peer] Invalid block payload: {str(error)}")

        except (
                BlockNotMinedError, DuplicateBlockError, BlockPreviousHashError,
                BlockHashMismatchError) as error:
                Logger.warning(f"[Interaction] Block validation failed: {str(error)}")


        except InvalidChainError as error:
            Logger.warning(f"[Interaction] Chain validation failed: {str(error)}")


    def __handleQueryInteraction(self, query: Query) -> Response:
        """Handles the incoming queris"""
        response: Response = Verifier.check(query)
        return response


    def __handleBlockBroadcast(self, block: Block, sender: str) -> None:
        self.__handleBlockInteraction(block)


    def __handleDiscoverMessage(self, message: DiscoverMessage) -> None:
        """
        A new peer asked for our connected peers list.
        Build a PeerSync response and send it back to the requester.
        """

        Logger.info(f"[Interaction ({self.me.name}) Handling a discovery message sent by {message.sender.name}]")
        # All the current node connections (Inbound + Outbound).
        # TODO: Implement the toAll checking.

        response: PeerSyncResponse = PeerSyncResponse(
            sender=self.me,
            connectedPeers=self.connections,
            to=message.sender
        )

        sender = NodeStorageManager.metadataToNodeConnection(message.sender, self.network.all_nodes)

        self.network.send_to_node(sender, {
            "action": Action.syncPeer.value,
            "data": response.model_dump(mode="json")
        })
        


    def already_connected(self, host: str, port: int ) -> bool:
        """Return True if the peer is already connected inbound or outbound."""

        connections: list[NodeMetadata] = self.connections

        for node in connections:
            if host == node.host and node.port == port:
                return True
        return False


    def __handlePeerSync(self, message: PeerSyncResponse) -> None:
        sender = message.sender
        nodes = message.connectedPeers

        Logger.info(f"[Interaction - Peer SYNC] Got {len(nodes)} from {sender.name}.")

        for node in nodes:
            host, port = node.host, node.port
            isSelf = (self.me.port == port and self.me.host == host)

            already = any(
                n.host == host and int(n.port) == port
                for n in self.network.all_nodes
            )

            if not isSelf and not already:
                self.network.connect_with_node(host=host, port=port)
                Logger.info(f"[Interaction - Peer-Sync Received] Connecting the node: {node.host}:{node.port}.")  
                time.sleep(0.5)

                # Verifing if current node is connected the shared node sucessfully.  
                if (self.nodeManager.nodeLookup(self.connections, host, port) in self.nodeManager.nodes):
                    Logger.info(f"[Interaction ({self.me.name})] Done connecting with the shared node ({node.name}) from ({sender.name}).")


    def __handleChainSyncRequest(self, message: ChainSyncRequest) -> None:
        self.chainSharing.send(request=message)
        ...           


    def __handleChainSyncResponse(self, message: ChainSyncResponse) -> None:
        self.chainSharing.receive(message)



    def __classifyInteraction(self, interaction: dict) -> Any:
        """Takes the incoming interaction and returns it's proper type (Block or Query)"""

        action: str = self.extractAction(interaction=interaction)
        
        data = interaction.get("data")



        if (action not in Action.getactionsaslist()):
            Logger.warning(f"[Interaction] Unknown action: got: {action}, available actions: {Action.getactionsaslist()}")
            return None



        if action == Action.registeration.value:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(data)

        if action == Action.BlockBroadcast.value:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(data)

        if action == Action.query.value:
            return Query.model_validate(data)

        if (action == Action.discover.value):
            return DiscoverMessage.model_validate(data)


        if (action == Action.syncPeer.value):
            return PeerSyncResponse.model_validate(data)

        if (action == Action.chainSyncRequest.value):
            return ChainSyncRequest.model_validate(data)

        if (action == Action.chainSyncResponse.value):
            return ChainSyncResponse.model_validate(data)