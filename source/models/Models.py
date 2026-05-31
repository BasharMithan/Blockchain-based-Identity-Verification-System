from datetime import datetime
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, model_validator, Field

from source.services.ledger import Ledger
from source.utils.generators import IDGenerator



class User(BaseModel):
    name: str
    nationalNumber: int
    phone: int
    age: int
    email: str
    birth: str
    HID: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "User":
        if (self.HID == ""):
            self.HID = IDGenerator.generateID(str(self.__dict__))
        return self




class Authority(BaseModel):
    name: str
    businessID: int
    AUTHID: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "Authority":
        if (self.AUTHID == ""):
            self.AUTHID = IDGenerator.generateID(str(self.__dict__))
        return self


class Identity(BaseModel):
    user: User
    issuer: Authority
    image: str
    credentialID: int
    CID: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "Identity":
        if (self.CID == ""):
            self.CID = IDGenerator.generateID(str(self.__dict__)) 
        return self


class CHID(BaseModel):
    user: User
    credential: Identity
    issuer: Authority
    chid: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "CHID":
        self.chid = IDGenerator.generateCHID(
            self.user.HID,
            self.credential.CID, 
            self.issuer.AUTHID
            )
        return self


class Block(BaseModel):
    """The standard schema that the user will fill,
    and prcessed and inserted to the ledger."""
    index: int
    data: CHID
    nonce: int = 0

    previousHash: str = ""
    date: str = str(datetime.now())
    hash: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "Block":

        # Automatically fill previousHash using Ledger if not provided
        try:
            if not self.previousHash:
                self.previousHash = Ledger().getLatestHash()
        except Exception:
            # fallback to 64 zeros if ledger access fails
            self.previousHash = "0" * 64

        # Generate hash after previousHash is set so it's included in the hash input
        if self.hash == "":
            self.hash = IDGenerator.generateID(str(self.__dict__))
        return self



class Response(Enum):
    appove = "APPROVED"
    decline = "DECLINED"


class Action(Enum):
    registeration = "REGISTERATION"
    query = "QWERY"
    hold = "HOLD"


class Qwery(BaseModel):
    user: User
    credential: Identity
       

class NodeConnectionType(Enum):
    inbound = "INBOUND"
    outbound = "OUTBOUND"

class NodeMetadata(BaseModel):
    nodeID: str
    host: str
    port: int
    connectionType: NodeConnectionType
    discoverDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
