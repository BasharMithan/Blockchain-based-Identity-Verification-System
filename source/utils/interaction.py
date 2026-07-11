import json, time
from p2pnetwork.node import Node
from typing import Any

from source.utils.nodeStorageManager import NodeStorageManager
from source.models.Models import (
    Block, Action, Response, DiscoverMessage,
    PeerSyncResponse, NodeMetadata, ChainSyncRequest, ChainSyncResponse,
    ChainLegthRequest, ChainLenghResponse
    )

from source.models.Models import Qwery as Query
from source.utils.logger import Logger
from source.services.blockManager import BlockManager
from source.services.verifier import Verifier
from source.services.chainSync import ChainSync

from source.errors import (
    DuplicateBlockError, InvalidBlockPayloadError, InvalidChainError,
    BlockHashMismatchError, BlockNotMinedError, BlockPreviousHashError)



class Interaction:
    def __init__(self, me: NodeMetadata, network: Node, interaction: dict, senderNode,
                 blockManager: BlockManager, nodeManager: NodeStorageManager, seenBlocks: set,
                 connections: list[NodeMetadata], receivedLedgers: list, receivedLengths: list) -> None:
        
        self.blockManager = blockManager
        self.nodeManager: NodeStorageManager = nodeManager
        self.senderNode = senderNode
        self.me = me
        self.connections: list = connections
        self.interaction = interaction
        self.seenBlocks: set = seenBlocks
        self.network = network

        self.chainSharing = ChainSync(
            ledger=self.blockManager.ledger,
            receivedLedgers=receivedLedgers,
            network=self.network,
            receivedLengths=receivedLengths,
            me=self.me)

        Logger.info(f"[Interaction - {self.me.name}] Got an interaction: {self.interaction.get('action')}.") # type: ignore



    def getAsBlock(self) -> Block | None:
        if self.extractAction() in (Action.registeration.value, Action.BlockBroadcast.value):
            blockDict = self.interaction.get("data")
            if isinstance(blockDict, str):
                try:
                    blockDict = json.loads(blockDict)
                except json.JSONDecodeError:
                    return None
            return Block.model_validate(blockDict)
        return None
        

    def extractAction(self) -> str:
         return self.interaction.get("action") # type: ignore
         
    
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
            

    def handle(self) -> None:
        """Handles the incoming interaction detected in the `node_message` function"""

        Logger.info(f"[Interaction] Starting the interaction handler.")

        decision = self.__classifyInteraction()


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

        elif (isinstance(decision, ChainLegthRequest)):
            self.__handleChainLengthRequest(decision)

        elif (isinstance(decision, ChainLenghResponse)):
            self.__handleChainLengthResponse(decision)


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


        self.network.send_to_node(self.senderNode, {
            "action": Action.syncPeer.value,
            "data": response.model_dump(mode="json")
        })
        Logger.info(
            f"""[Interaction - Discover Response] Sending {
            len(self.connections)
            } peers to the peer {
                self.senderNode.host}:{self.senderNode.port}.""")


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


    def __handleChainLengthRequest(self, message: ChainLegthRequest) -> None:

        self.chainSharing.receiveChainLengthRequest(message)


    def __handleChainLengthResponse(self, message: ChainLenghResponse) -> None:

        self.chainSharing.receiveLengthResponse(message) # TODO: Implement this function


    def __classifyInteraction(self) -> Any:
        """Takes the incoming interaction and returns it's proper type (Block or Query)"""

        action: str = self.extractAction()
        
        data = self.interaction.get("data")

        print(f"({self.me.name}) Got an interaction: {action}")

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


        if (action == Action.chainLenghRequest.value):
            return ChainLegthRequest.model_validate(data)
        
        if (action == Action.chainLenghResponse.value):
            return ChainLenghResponse.model_validate(data)
