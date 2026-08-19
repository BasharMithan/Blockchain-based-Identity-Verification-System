from fastapi import APIRouter, HTTPException

from services.peer import Peer
from models.APIModels import APIRegisterationRequest, VerificationRequest
from API.APIServices import APICommunication
from errors.APIErrors import APIError


def buildRouter(peer: Peer) -> APIRouter:
    router = APIRouter()
    communication = APICommunication(peer)

    @router.post("/register", status_code=201)
    def register(payload: APIRegisterationRequest):

        result = communication.processBlockRegisterationRequest(payload)
        
        if isinstance(result, APIError):
            raise HTTPException(status_code=409, detail=result.message)
        
        return result

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