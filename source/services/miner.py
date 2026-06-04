from source.models.Models import Block
from source.utils.logger import Logger

class Miner:
    DIFFICULTY = 4  # number of leading zeros required
    TARGET = "0" * DIFFICULTY

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

            if block.hash.startswith(Miner.TARGET):
                Logger.info(
                    f"[Miner] Block {block.index} mined after "
                    f"{attempts} attempts. Nonce: {block.nonce}"
                )
                return block

            block.nonce += 1
            attempts += 1



