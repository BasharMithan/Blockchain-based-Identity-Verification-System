from fastapi import APIRouter

from source.utils.blocks.blockManager import BlockManager
from source.services.peer import NewPeer
from source.models.Models import NodeMetadata, Identity
from source.models.APIModels import RegisterationRequest, VerificationRequest
from source.API.APIServices import APICommunication


def buildRouter(peer: NewPeer) -> APIRouter:
    router = APIRouter()
    communication = APICommunication(peer)

    @router.post("/register", status_code=201)
    def register(payload: RegisterationRequest):
        communication.processBlockRegisterationRequest(payload)

    @router.post("/verify")
    def verify(payload: VerificationRequest):
        ...


    @router.get("/chain")
    def chain():
        return APICommunication.sendChain(node=peer.me, blockManager=peer.blockManager)

    @router.get("/status")
    def status():
        return APICommunication.sendNodeStatus(metaData=peer.me, blockManager=peer.blockManager)

    return router