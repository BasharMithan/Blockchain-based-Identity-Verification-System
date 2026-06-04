from source.models.Models import Block
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.services.miner import Miner


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""
    def __init__(self) -> None:
        self.ledger = Ledger()
        self.miner = Miner()


    def registerBlock(self, block: Block) -> None:
            minedBlock = self.miner.mine(block)
            self.ledger.insertBlock(minedBlock)
            Logger.info(f"[Block Manager] Block ({block.hash}) inserted the ledger.") 


