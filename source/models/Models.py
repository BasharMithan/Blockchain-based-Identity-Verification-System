from datetime import datetime
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, model_validator, Field

from source.utils.generators import IDGenerator

DIFFICULTY = "0" * 4

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
    data: CHID

    index: int = 0
    nonce: int = 0
    previousHash: str = ""
    date: str = str(datetime.now())
    hash: str = ""

    @model_validator(mode="after")
    def __post_init__(self) -> "Block":

        # Do not mutate persisted block indexes during model validation.
        # Index assignment for new blocks is handled explicitly by the
        # Block creator (BlockManager / Ledger) before mining/insertion.
        return self

    def computeHash(self) -> str:
        """Recomputable hash that includes nonce."""
        content = f"{self.index}{self.data.chid}{self.nonce}{self.previousHash}"
        return IDGenerator.generateID(content)

    # In Block (Models.py)

    def isHashValid(self) -> bool:
        """Hash matches a recomputation of this block's contents."""
        return self.hash == self.computeHash()

    def isMined(self) -> bool:
        """Hash satisfies the proof-of-work target."""
        return self.hash.startswith(DIFFICULTY)



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
