from source.models.Models import Block
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.utility_function import LedgerUtilities

from source.errors import DuplicateBlockError, InvalidChainError


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""

    def __init__(self, filePath) -> None:
        self.ledger = Ledger(filePath)
        self.miner = Miner()

    def registerBlock(self, block: Block) -> Block:
        
        block.index = LedgerUtilities.getLedgerLength(self.ledger.filePath)
        block.previousHash = LedgerUtilities.getLatestHash(self.ledger.filePath)
        

        if self.checkIfBlockExists(block.data.chid, self.ledger.filePath):
            Logger.warning(f"[Block validation] The block {block.index} already in the ledger!")
            raise DuplicateBlockError(block.data.chid)

        minedBlock = self.miner.mine(block)

        if not self.__validChain():
            raise InvalidChainError("Chain failed integrity check before insert.")


        self.ledger.insertBlock(minedBlock)
        return minedBlock

    def receiveBlock(self, block: Block) -> Block:
        if self.checkIfBlockExists(block.data.chid, self.ledger.filePath):
            raise DuplicateBlockError(block.data.chid)

        blockValidation = BlockValidator()
        blockValidation.validate(block, self.ledger.blocks[-1]["hash"])

        self.ledger.insertBlock(block)
        Logger.info(f"[Block Validation] Received block {block.index} inserted.")
        return block

    def __validChain(self) -> bool:
        return ChainValidation(self.ledger.filePath).validate()

    @staticmethod
    def checkIfBlockExists(targetCHID: str, filePath) -> bool:
        ledger: list = LedgerUtilities.readLedger(filePath)
        for block in ledger:
            if targetCHID == block["data"]["chid"]:
                return True
        return False