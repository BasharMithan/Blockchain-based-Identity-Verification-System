from source.models.Models import Block
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.utility_function import LedgerUtilities


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""
    def __init__(self) -> None:
        self.ledger = Ledger()
        self.miner = Miner()


    def registerBlock(self, block: Block) -> None | Block:
        print(f"[BlockManager] registerBlock called for block candidate index={block.index}")
        # computed hash includes the final previousHash and index.
        block.index = LedgerUtilities.getLedgerLength()
        block.previousHash = LedgerUtilities.getLatestHash()

        if self.checkIfBlockExists(block.data.chid):
            Logger.warning(f"[Block validation] The block {block.index} aredy in the ledger !")
            return None
        
        minedBlock = self.miner.mine(block)

        
        if (self.__valid()):
            self.ledger.insertBlock(minedBlock)
            return minedBlock
        else:
            return None

    def receiveBlock(self, block: Block) -> None | Block:
        blockValidation = BlockValidator()
        Logger.info(f"[Block Validation] Received block {block.index}.")

        print(f"Previous hash of the {block.index} -> {LedgerUtilities.getLatestHash()}")
        if not blockValidation.validate(block, LedgerUtilities.getLatestHash()):
            Logger.warning(f"[Block Validation] Recived block {block.index} is not valid !")
            return None

        Logger.info(f"[Block Validation] Received block {block.index} is valid and ready to be inserted to the ledger.")
        self.ledger.insertBlock(block)
        return block


    def __valid(self) -> bool:
        chainValidator = ChainValidation()
        isValid: bool = chainValidator.validate()
        return isValid

    @staticmethod
    def checkIfBlockExists(targetCHID: str) -> bool:
        ledger: list = LedgerUtilities.readLedger()
        if (len(ledger) == 0):
            return False

        for block in ledger:
            if targetCHID == block["data"]["chid"]:
                return True
        return False
    