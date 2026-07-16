from fastapi import APIRouter

from source.utils.blocks.blockManager import BlockManager
from source.models.Models import NodeMetadata, Identity
from source.models.APIModels import RegisterationRequest, VerificationRequest
from source.API.APIServices import APICommunication


def buildRouter(blockManager: BlockManager, me: NodeMetadata) -> APIRouter:
    router = APIRouter()

    @router.post("/register", status_code=201)
    def register(payload: RegisterationRequest):
        ...

    @router.post("/verify")
    def verify(payload: VerificationRequest):
        ...


    @router.get("/chain")
    def chain():
        return APICommunication.sendChain(node=me, blockManager=blockManager)

    @router.get("/status")
    def status():
        return APICommunication.sendNodeStatus(metaData=me, blockManager=blockManager)

    return router