from pydantic import BaseModel
from enum import Enum

from source.models.Models import NodeMetadata



class UserAPIModel(BaseModel):
    name: str
    nationalNumber: int
    phone: int
    age: int
    email: str
    birth: str



class IdentityAPIModel(BaseModel):
    image: str
    identityID: int


class IssuerAPIModel(BaseModel):
    name: str
    issuerID: int


class APIRegisterationRequest(BaseModel):
    user: UserAPIModel
    credential: IdentityAPIModel
    issuer: IssuerAPIModel 

class APIRegisterationResponse(BaseModel):
    response: str


class VerificationRequest(BaseModel):
    user: str # User.name
    UserID: int # User.nationalNumber
    credentialID: int # Identity.IdentityID
    issuer: str # Authority.name
    issuerID: int # Authority.businessID

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


class IDTyping(Enum):
    user = "USER"
    identity = "IDENTITY"
    authority = "AUTHORITY"