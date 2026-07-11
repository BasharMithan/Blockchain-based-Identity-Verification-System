from p2pnetwork.node import Node

from source.services.ledger import Ledger
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.nodeStorageManager import NodeStorageManager
from source.models.Models import (ChainSyncResponse, ChainSyncRequest, Action, NodeMetadata,
                                  ChainLenghResponse, ChainLegthRequest)
from source.utils.utility_function import LedgerUtilities



class ChainSync:
    """The ledger sharing mechanism, shares the local ledger with the new nodes,
    and receives the ledger sharing requests if it's the new node."""

    def __init__(self, ledger: Ledger, network: Node, receivedLedgers: list, receivedLengths: list, me: NodeMetadata) -> None:
        self.ledger = ledger
        self.network = network # Node object to have the ability to send payloads to the network.
        self.receivedLedgers: list = receivedLedgers
        self.receivedLengths = receivedLengths
        self.me: NodeMetadata = me
    

        self.expectedResponses: int = 0 # Keeps track of the number of connected nodes. 

    def request(self) -> None:
        """Requests the ledger from all the connected nodes. If the current node
           is a new node, or the ledger seems to be invalid or the whole ledger
           is missing.
           """

        self.expectedResponses = len(self.network.all_nodes)

        message = ChainSyncRequest(sender=self.me)

        # Requsting the ledger to all connected nodes. TODO: Implement the conditions to execute this function.
        self.network.send_to_nodes({
            "action": Action.chainSyncRequest.value,
            "data": message.model_dump(mode="json")
        }, exclude=[NodeStorageManager.metadataToNodeConnection(self.me, self.network.all_nodes)]) 



    def receive(self, response: ChainSyncResponse) -> None:
        """Reads the chain sync response message, saves the received ledger with all other
        received ledger, the chooses the best ledger among all the received ledger to be set
        as the ledger of the current node."""

        # Store the received ledger.
        self.receivedLedgers.append(response.ledger)

        # Check if the main contidion to say that the request has been sent to all nodes.
        if (len(self.receivedLedgers) >= self.expectedResponses):
            
            choosenChain = self.__chooseBestLedger(self.receivedLedgers) 
            print(f"{response.sender.name} -> {self.me.name} a ledger with {len(choosenChain)} blocks.")

            self.ledger.updateLedger(choosenChain) if self.compareReceivedChain(choosenChain) else None
            print(f"[{self.me.name}] Ledger is updated from a {len(self.ledger.blocks)} to a ledger with {len(choosenChain)}.")



    def send(self, request: ChainSyncRequest) -> None:
        """Reads the received request, and responds to it."""

        # sender: NodeMetadata = request.sender # TODO: Convert it to NodeConnection

        copiedLedger: list = self.copyChain()

        response: ChainSyncResponse = ChainSyncResponse(sender=self.me, ledger=copiedLedger, length=len(copiedLedger))

        # Checks the validity of the local ledger before sending it.
        if self.validateBeforeSending(copiedLedger):

            # The given node is a NodeMetadata, converting it to NodeConnection
            targetNode = NodeStorageManager.metadataToNodeConnection(request.sender, self.network.all_nodes)

            # Sending a copy of the local ledger to the node requested it.
            self.network.send_to_node(targetNode, {
                "action": Action.chainSyncResponse.value,
                "data": response.model_dump(mode="json")
                })
            

    def compareReceivedChain(self, receivedChain: list) -> bool:
        """Compares the received (choosen chain) chain with the local chain,
        if the received chain is more valid than the local chain we replace it.
        Else, nothing happens."""

        localChain = self.ledger.blocks

        chainValidator = ChainValidation(receivedChain)

        if (chainValidator.validate()) and len(receivedChain) > len(localChain):
            return True
        return False
            


    def receiveChainLengthRequest(self, lengthRequest: ChainLegthRequest) -> None:
        "Receives the chain length request, and responses with the chain length response."

        localChainLength = len(self.ledger.blocks)
        sender = NodeStorageManager.metadataToNodeConnection(lengthRequest.sender, self.network.all_nodes)
        response = ChainLenghResponse(sender=self.me, length=localChainLength)

        self.network.send_to_node(sender, {
            "action": Action.chainLenghResponse.value,
            "data": response.model_dump(mode="json") 
        })


    def requestLength(self) -> None:
        """Requesting the length of the nodes' lengths before sending the chain sync request.
        Length request is a lightweight request, let's the node get the lengths first
        to check if there is blocks are missing,
        or it has been disconnected for a while and missed some blocks."""

        request = ChainLegthRequest(sender=self.me)

        self.network.send_to_nodes({
            "action": Action.chainLenghRequest.value,
            "data": request.model_dump(mode="json")
        })


    def receiveLengthResponse(self, response: ChainLenghResponse) -> None:
        "Takes the chain length response, and adds it to the `receivedLengths` list."

        self.receivedLengths.append(response) 



    def verifiy(self, leger: list) -> bool:
        """Checks the validity of the received chain."""
        ...


    def __chooseBestLedger(self, ledgers: list) -> list:
        """Takes the collection of chains, and returns what it calls **the best chain**.
           The best chain is the chain that is valid, and is the longest (Contains more nodes).
           If all the chains are equl, it chooses any
           (Only if all the received chains are equl and all valid)."""

        # Loop through the received ledgers and extract the valid ones.
        validLedgers = [vl for vl in ledgers if self.__validateReceivedLedger(vl)]

        if not validLedgers:
            return self.ledger.blocks # Keep the local ledger if the validLedgers list is empty.

        return max(validLedgers, key=len) # Longest valid chain wins.
    

    def __validateReceivedLedger(self, ledger: list) -> bool:
        """Inital step after receiving a ledger. Verifies the received ledger."""
        valid: bool = ChainValidation(ledger).validate()
        return valid

    def copyChain(self) -> list:
        """Returns a deep copy of the current stored ledger `ledger.nodes`."""
        import copy

        local = self.ledger.blocks
        return copy.deepcopy(local)


    def validateBeforeSending(self, ledger: list) -> bool:
        """Last step in the chain sync response. Checks the validity of the chain before
        sending to the node that requested it, if it's not valid, we dont send it. 
        # TODO: Implenent the message that must be sent if the local ledger is not valid."""

        chainValidation = ChainValidation(self.ledger.blocks)
        return chainValidation.validate()
