from source.models.Models import Block
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.utility_function import LedgerUtilities


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""
    def __init__(self) -> None:
        self.ledger = Ledger()
        self.miner = Miner()
        self.chainValidator = ChainValidation()


    def registerBlock(self, block: Block) -> None:
        # Assign the correct index and previousHash before mining so the
        # computed hash includes the final previousHash and index.
        block.index = LedgerUtilities.getLedgerLength()
        block.previousHash = LedgerUtilities.getLatestHash()
        minedBlock = self.miner.mine(block)
        
        self.ledger.insertBlock(minedBlock)
        Logger.info(f"[Block Manager] Block ({block.index}) inserted the ledger.") 


    