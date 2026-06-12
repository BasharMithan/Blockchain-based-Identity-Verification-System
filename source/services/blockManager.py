from source.models.Models import Block
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.utility_function import LedgerUtilities

from source.errors import (
    DuplicateBlockError, 
    InvalidChainError)


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""
    def __init__(self) -> None:
        self.ledger = Ledger()
        self.miner = Miner()


    def registerBlock(self, block: Block) ->  Block:
        print(f"[BlockManager] registerBlock called for block candidate index={block.index}")
        # computed hash includes the final previousHash and index.
        block.index = LedgerUtilities.getLedgerLength()
        block.previousHash = LedgerUtilities.getLatestHash()

        if self.checkIfBlockExists(block.data.chid):
            Logger.warning(f"[Block validation] The block {block.index} aredy in the ledger !")
            raise DuplicateBlockError(block.data.chid)
        
        minedBlock = self.miner.mine(block)

        
        if not self.__validChain():
                raise InvalidChainError(f"[Block Manager] Chain is invalid")
        
        self.ledger.insertBlock(minedBlock)
        return minedBlock


    def receiveBlock(self, block: Block) ->  Block:
        blockValidation = BlockValidator()
        Logger.info(f"[Block Validation] Received block {block.index}.")

        blockValidation.validate(block, LedgerUtilities.getLatestHash())
        
        Logger.info(f"[Block Validation] Received block {block.index} is valid and ready to be inserted to the ledger.")
        self.ledger.insertBlock(block)
        return block


    def __validChain(self) -> bool:
        chainValidator = ChainValidation()
        return chainValidator.validate()

    @staticmethod
    def checkIfBlockExists(targetCHID: str) -> bool:
        ledger: list = LedgerUtilities.readLedger()
        if (len(ledger) == 0):
            return False

        for block in ledger:
            if targetCHID == block["data"]["chid"]:
                return True
        return False
    