from p2pnetwork.node import NodeConnection

from source.models.APIModels import VerificationRequest, NodeStatus, ChainModel, RegisterationRequest
from source.services.peer import NewPeer
from source.models.Models import NodeMetadata
from source.services.verifier import Verifier
from source.utils.blocks.blockManager import BlockManager
from source.utils.chain_validation import ChainValidation


class APICommunication:
    "Responsable for responding to API messages and nalysing the incoming data from the API"
    def __init__(self, peer: NewPeer) -> None:
        self.peer = peer
        pass


    @staticmethod
    def processVerificationRequest(verificationRequest: VerificationRequest, blockManager: BlockManager, me: NodeMetadata) -> None:
        ...

    def processBlockRegisterationRequest(self, registerationRequest: RegisterationRequest) -> None:
        block = registerationRequest.block
        self.peer.registerBlock(block)


    @staticmethod
    def sendNodeStatus(metaData: NodeMetadata, blockManager: BlockManager) -> NodeStatus:
        "Returns the NodeStatus model to the API router."

        name: str = metaData.name
        host, port = metaData.host, metaData.port

        ledger: list = blockManager.ledger.blocks
        cv = ChainValidation(ledger)

        chainValidity: bool = cv.validate()

        blocksCount: int = len(ledger)

        return NodeStatus(
            name=name,
            host=host,
            port=port,
            chainValidity=chainValidity,
            blocksCount=blocksCount
        )


    @staticmethod
    def sendChain(node: NodeMetadata, blockManager: BlockManager) -> ChainModel:
        return ChainModel(sender=node, chain=blockManager.ledger.blocks)