import json
from pathlib import Path

from source.utils.logger import Logger
from source.utils.chain_validation import ChainValidation
from source.services.miner import Miner
from source.models.Models import Block, CHID, Authority, User, Identity

class Ledger:

    def __init__(self) -> None:
        # store Block instances (or loaded dicts); start empty
        self.blocks: list = [dict]
        self.filePath: Path = Path("storage/.ledger.json")
        self.__createFileIfnotExist()
        self.__loadLedger()
        self.miner = Miner()
        if (len(self.blocks) == 0): self.__generateGensisBlock()



    def __loadLedger(self) -> None:
        """Reads the values from the json file and loads them into `self.blocks`.

        Currently loads raw JSON structures (dicts/lists). Reconstructing
        dataclass `Block` objects could be added later if needed.
        """
        try:
            text = self.filePath.read_text(encoding='utf-8').strip()
           
            if not text:
                Logger.warning("[Ledger] The ledger is empty !")
                
                self.__generateGensisBlock()
                Logger.info("[Ledger] The Gensis block is generated and inserted to the ledger as the first block.")
                return

            data = json.loads(text)
            if isinstance(data, list):
                self.blocks = data
            else:
                self.blocks = [data]
        except Exception:
            self.blocks = []

    def __createFileIfnotExist(self) -> None:
        if not self.filePath.is_file():
            # ensure parent exists
            self.filePath.parent.mkdir(parents=True, exist_ok=True)
            self.filePath.write_text('', encoding='utf-8')

    def insertBlock(self, targetBlock: Block) -> None:

        block = targetBlock

        block.previousHash = self.getLatestHash()

        minedBlock = self.miner.mine(block)

        self.chainValidator = ChainValidation()
        validLedger: bool = self.chainValidator.validate()

        if (self.__checkIfBlockExists(minedBlock)):
            Logger.warning(f"Block with CHID: {minedBlock.data.chid} already exists !")
            return
        
        if (not validLedger):
            Logger.warning("[Chain Validation - Ledger] Chain is invalid !")

        blockAsDict =  json.loads(Block.model_dump_json(block))
        
        self.blocks.append(blockAsDict)
        self.__writeBlockToLedger(blockAsDict)
        self.__loadLedger()



    def __writeBlockToLedger(self, block: dict) -> None:
        with open(self.filePath, "w", encoding="utf-8") as ledgerFile:
            json.dump(self.blocks, ledgerFile, indent=4)
        print(block)
        Logger.info(f"Block with CHID {block["data"]} inserted successfully. ")


        
    def getLatestBlock(self):
        blocks: list = []
        try:
            with open(self.filePath, "r", encoding='utf-8') as ledgerFile:
                data = json.load(ledgerFile)
                for block in data:
                    blocks.append(block)
            return blocks[-1]
        except json.JSONDecodeError:
            return None
    
    
    def getLatestHash(self) -> str:
        """
        Return the latest block's hash as a hex string.
        Falls back to 64 zeros when no blocks or an error occurs.
        Handles both dict-shaped blocks and dataclass/objects with a 'hash' attribute.
        """
        zero_hash = "0" * 64
        try:
            # Prefer in-memory ledger
            if self.blocks:
                latest = self.blocks[-1]
            else:
                latest = self.getLatestBlock()
                if not latest:
                    return zero_hash
            if isinstance(latest, dict):
                return latest.get("hash", zero_hash)
            return getattr(latest, "hash", zero_hash)
        except Exception:
            return zero_hash


    def allBlocks(self) -> list:
        return self.blocks


    def chidExists(self, target_chid: str) -> bool:
        for block in self.blocks:
            if isinstance(block, dict):
                data = block.get("data")
                if isinstance(data, dict) and data.get("chid") == target_chid:
                    return True
            else:
                chid_value = getattr(getattr(block, "data", None), "chid", None)
                if chid_value == target_chid:
                    return True
        return False

    
    def __checkIfBlockExists(self, targetBlock: Block) -> bool:
        targetCHID = targetBlock.data.chid

        for block in self.blocks:
            if targetCHID == block["data"]["chid"]:
                return True
        return False


    def __generateGensisBlock(self) -> None:
        user=User(name="Gensis-Block", nationalNumber=0, phone=0, age=0, email="", birth="")
        auth = Authority(name="", businessID=0)
        doc = Identity(user=user, issuer=auth, image="", credentialID=0)
        chid = CHID(user=user, credential=doc, issuer=auth)

        block = Block(data=chid, hash="0"*64)

        self.insertBlock(block)

