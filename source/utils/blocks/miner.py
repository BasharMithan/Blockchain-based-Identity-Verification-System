from models.Models import Block
from utils.logger import Logger
from models.constants import TARGET

class Miner:

    @staticmethod
    def mine(block: Block) -> Block:
        """
        Increments block.nonce until block.hash starts 
        with DIFFICULTY leading zeros.
        Returns the solved block.
        """

        Logger.info(f"[Miner]Mining block {block.index}...")
        attempts = 0
        
        while True:
            block.hash = block.computeHash()

            if block.hash.startswith(TARGET):
                Logger.info(
                    f"[Miner] Block {block.index} mined after "
                    f"{attempts} attempts. Nonce: {block.nonce}"
                )
                return block

            block.nonce += 1
            attempts += 1



