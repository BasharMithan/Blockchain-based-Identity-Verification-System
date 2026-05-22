from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from source.utils.generators import IDGenerator 
from source.utils.ledger import Ledger

@dataclass
class HashedValue:
    # id: str = field(init=False)

    def generateID(self) -> str:
        return IDGenerator.generateID(str(self.__dict__))

@dataclass
class User(HashedValue):
    name: str
    nationalNumber: int
    phone: int
    age: int
    email: str
    birth: str

    def __post_init__(self):
            self.HID = self.generateID()



@dataclass
class Authority(HashedValue):
    name: str
    businessID: int

    def __post_init__(self) -> None:
            self.AUTHID = self.generateID()

@dataclass
class Identity(HashedValue):
    user: User
    issuer: Authority
    image: str
    credentialID: int

    def __post_init__(self):
        self.CID = self.generateID() 


@dataclass
class CHID:
    user: User
    credential: Identity
    issuer: Authority

    def __repr__(self) -> str:
        return IDGenerator.generateCHID(
            self.user.HID,
            self.credential.CID, 
            self.issuer.AUTHID
            )


@dataclass
class Block:
    """The standard schema that the user will fill,
    and go in the Blockchain network."""
    index: int
    data: CHID
    nonce: int = 0

    previousHash: str = ""
    date: str = str(datetime.now())
    hash: str = ""

    def __post_init__(self):
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



class Response(Enum):
    appove = "APPROVED"
    decline = "DECLINED"

# class InitalBlock(Enum):
#     initalUser = User("", 0, 0, 0, "", "")
#     initalIssuer = Authority("", 0)
#     initalDoc = Identity(initalUser, initalIssuer, "", 0)
#     initalBlock = Block(0, CHID(initalUser, initalDoc, initalIssuer), "0"*64)