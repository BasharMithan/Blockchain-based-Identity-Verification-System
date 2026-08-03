from source.models.APIModels import (VerificationRequest, NodeStatus,
                                     ChainModel, APIRegisterationRequest)
from source.services.peer import Peer
from source.models.Models import NodeMetadata, Identity, Authority, Block, CHID, Query, Response
from source.services.verifier import Verifier, User
from source.utils.blocks.blockManager import BlockManager
from source.utils.chain_validation import ChainValidation



class APICommunication:
    "Responsable for responding to API messages and nalysing the incoming data from the API"
    def __init__(self, peer: Peer) -> None:
        self.peer = peer
        self.verifier = Verifier()
        pass


    
    def processVerificationRequest(self, verificationRequest: VerificationRequest) -> Response | None:
        user = self.peer.ledger.findUser(verificationRequest.UserID)
        credential = self.peer.ledger.findCredential(verificationRequest.credentialID)
        issuer = self.peer.ledger.findIssuer(verificationRequest.issuerID)
        if user and credential and issuer:
            query = Query(user=user, credential=credential, issuer=issuer)
            return self.verifier.check(query)



    def processBlockRegisterationRequest(self, registerationRequest: APIRegisterationRequest) -> Block | None:
        "Takes the `RegisterationRequest` received from the API, builds the block and registers it on the chain."

        user = User(
            name=registerationRequest.user.name,
            age=registerationRequest.user.age,
            nationalNumber=registerationRequest.user.nationalNumber,
            phone=registerationRequest.user.phone,
            email=registerationRequest.user.email,
            birth=registerationRequest.user.birth,
            HID=""
            )

        issuer = Authority(
            name=registerationRequest.issuer.name,
            businessID=registerationRequest.issuer.issuerID,
            AUTHID=""
        )

        doc = Identity(
            image=registerationRequest.credential.image,
            credentialID=registerationRequest.credential.identityID,
            CID=""
        )

        block = Block(
            data=CHID(
                user=user,
                credential=doc,
                issuer=issuer,
                chid=""
            )
        )

        return self.peer.registerBlock(block)



    
    def sendNodeStatus(self) -> NodeStatus:
        "Returns the NodeStatus model to the API router."

        name: str = self.peer.title
        host, port = self.peer.host, self.peer.port

        ledger: list = self.peer.ledger.blocks
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



class Authorization:
    def __init__(self) -> None:
        pass

    def CHIDVerification(self, chid: str) -> bool:
        ...
