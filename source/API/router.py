from fastapi import APIRouter

from source.services.peer import Peer
from source.models.APIModels import APIRegisterationRequest, VerificationRequest
from source.API.APIServices import APICommunication


def buildRouter(peer: Peer) -> APIRouter:
    router = APIRouter()
    communication = APICommunication(peer)


    @router.post("/register", status_code=201)
    def register(payload: APIRegisterationRequest):
        return communication.processBlockRegisterationRequest(payload)


    @router.post("/check")
    def check(payload: VerificationRequest):
        
       return communication.processVerificationRequest(payload)


    @router.get("/chain")
    def chain():
        return communication.sendChain(node=peer.me, blockManager=peer.blockManager)

    @router.get("/status")
    def status():
        return communication.sendNodeStatus()



    return router