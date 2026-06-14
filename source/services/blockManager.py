from source.models.Models import Block
from source.models.constants import LEDGER_PATH
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.utility_function import LedgerUtilities

from source.errors import DuplicateBlockError, InvalidChainError


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""

    def __init__(self, filePath=LEDGER_PATH) -> None:
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
            raise InvalidChainError("[Block Manager] Chain is invalid")

        self.ledger.insertBlock(minedBlock)
        return minedBlock

    def receiveBlock(self, block: Block) -> Block:
        blockValidation = BlockValidator()
        Logger.info(f"[Block Validation] Received block {block.index}.")

        blockValidation.validate(block, LedgerUtilities.getLatestHash(self.ledger.filePath))

        Logger.info(f"[Block Validation] Received block {block.index} is valid and ready to be inserted.")
        self.ledger.insertBlock(block)
        return block

    def __validChain(self) -> bool:
        return ChainValidation(self.ledger.filePath).validate()

    @staticmethod
    def checkIfBlockExists(targetCHID: str, filePath=LEDGER_PATH) -> bool:
        ledger: list = LedgerUtilities.readLedger(filePath)
        for block in ledger:
            if targetCHID == block["data"]["chid"]:
                return True
        return False