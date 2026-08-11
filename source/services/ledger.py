import json
import threading
from pathlib import Path
from typing import Any 

from utils.logger import Logger
from utils.chain_validation import ChainValidation
from utils.blocks.miner import Miner
from models.Models import Block, CHID, Authority, User, Identity
from models.APIModels import UserAPIModel, IdentityAPIModel

from errors import (
    LedgerNotFoundError,
    LedgerCorruptError,
    InvalidChainError,
    GenesisBlockError,
    DuplicateBlockError,
    )

class Ledger():

    def __init__(self, filePath: Path) -> None:
        # store Block instances (or loaded dicts); start empty
        self.blocks: list[dict[str, Any]] = []
        self.filePath: Path = filePath
        self._lock = threading.RLock() # A lock to prevent concurrent insert/write race in the same ledger instance.

        self.miner = Miner()

        self.shouldRequestChain = False

        self.__initLedger()
        self.__loadLedger()
        self.__ensureGenesis()


    def __initLedger(self) -> None:
        if not self.filePath.is_file():
            self.__createFileIfnotExist()
            self.__generateGensisBlock()


    def __ensureGenesis(self) -> None:
        if len(self.blocks) == 0:
            self.__generateGensisBlock()



    def __loadLedger(self) -> None:
        """Reads the values from the json file and loads them into `self.blocks`.

        Currently loads raw JSON structures (dicts/lists). Reconstructing
        dataclass `Block` objects could be added later if needed.
        """
        try:
            text = self.filePath.read_text(encoding='utf-8').strip()
           
            if not text:
                Logger.warning("[Ledger] The ledger is empty !")
                return

            data = json.loads(text)
            if isinstance(data, list):
                self.blocks = data
            else:
                self.shouldRequestChain = True
                raise LedgerCorruptError(str(self.filePath))
            
        except json.JSONDecodeError as error:
            self.shouldRequestChain = True
            raise LedgerCorruptError(str(self.filePath)) from error


    def __createFileIfnotExist(self) -> None:
            try:
                # ensure parent exists
                self.filePath.parent.mkdir(parents=True, exist_ok=True)
                self.filePath.write_text('', encoding='utf-8')
            except OSError as error:
                self.shouldRequestChain = True
                raise LedgerNotFoundError(str(self.filePath)) from error


    def insertBlock(self, block: Block) -> Block:
        with self._lock:
            chainValidation = ChainValidation(self.blocks)

            if not chainValidation.validate():
                raise InvalidChainError("Chain failed integrity check before insert.")

            blockAsDict = json.loads(Block.model_dump_json(block))
            blockChid = blockAsDict.get("data", {}).get("chid")

            if any(existing.get("data", {}).get("chid") == blockChid for existing in self.blocks):
                Logger.warning(f"[Ledger] Block with CHID {blockChid} already exists; refusing duplicate insert.")
                raise DuplicateBlockError(blockChid)

            self.blocks.append(blockAsDict)
            self.__writeBlockToLedger(blockAsDict)

            return block


    def __writeBlockToLedger(self, block: dict) -> None:
        with open(self.filePath, "w", encoding="utf-8") as ledgerFile:
            json.dump(self.blocks, ledgerFile, indent=4)
        Logger.info(f"Block with CHID {block['data']} inserted successfully. ")


    def allBlocks(self) -> list:
        return self.blocks


    def findUser(self, nationalNumber: int, username: str) -> User | None:
        "Takes the user from the API block registeration request, returns the actual User (with HID)"
        for blockDict in self.blocks:
            block = Block.model_validate(blockDict)

            if nationalNumber == block.data.user.nationalNumber and username == block.data.user.name:
                return block.data.user
        return None


    def findCredential(self, credentialID: int) -> Identity | None:
        "Finds the in-chain credential and returns it."

        for blockDict in self.blocks:
            block = Block.model_validate(blockDict)

            if credentialID == block.data.credential.credentialID:
                return block.data.credential
        return None        


    def findIssuer(self, issuerID: int, issuerName: str) -> Authority | None:
        "Finds the on-chain issuer"

        for blockDict in self.blocks:
            block = Block.model_validate(blockDict)

            if issuerID == block.data.issuer.businessID and issuerName == block.data.issuer.name:
                return block.data.issuer


    def getLatestHash(self) -> str:
        "Return the latest block's hash."
        return self.blocks[-1]["hash"]
            

        


    
    def __generateGensisBlock(self) -> None:
        user=User(name="Gensis-Block", nationalNumber=0, phone=0, age=0, email="", birth="")
        auth = Authority(name="", businessID=0)
        doc = Identity(image="", credentialID=0)
        chid = CHID(user=user, credential=doc, issuer=auth)

        block = Block(data=chid)
        # Ensure genesis block has correct index and previousHash before mining
        block.index = 0
        block.previousHash = "0"*64

        try:

            mined = self.miner.mine(block)
            self.insertBlock(mined)
        except Exception as error:
            self.shouldRequestChain = True
            raise GenesisBlockError(str(error)) from error


    def updateLedger(self, newLedger: list) -> None:
        """Defined to meet the requirements of the `ChainSync` class, where it replaces
        the current ledger, with a ledger that has been choosen by the `ChainSync` class.
        """
        self.blocks = newLedger

        with open(self.filePath, "w", encoding="utf-8") as ledgerFile:
            json.dump(newLedger, ledgerFile, indent=4)

        self.shouldRequestChain = False


