from pydantic import BaseModel
from source.models.Models import Block
from source.models.Models import NodeMetadata



class RegisterationRequest(BaseModel):
    ...

class RegisterationResponse(BaseModel):
    ...


class VerificationRequest(BaseModel):
    ...

class VerificationResponse(BaseModel):
    ...

class NodeStatus(BaseModel):
    name: str
    host: str
    port: int
    chainValidity: bool
    blocksCount: int


class ChainModel(BaseModel):
    sender: NodeMetadata
    chain: list