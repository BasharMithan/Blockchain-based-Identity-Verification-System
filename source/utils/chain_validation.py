
import json

from source.utils.utility_function import readLedger
from source.utils.logger import Logger
from source.models.Models import Block
from source.services.miner import Miner


class ChainValidation:
    """Validates if the chain is valid based on 3 important checks:
        1. Check if the content of a block match the hash assigned to that block,
        by recomputing the hash of these content.
        2. Check if all the blocks' hash starts with 4 zeros (Mined).
        3. Check if the hash of the N block matches the hash of the N + 1 block."""

    def __init__(self) -> None:
        self.ledger = readLedger()
        self.miner = Miner()


        Logger.info("[Chain Validation] Initalizing the chain validator.")

        if (len(self.ledger) == 0):
            Logger.warning("[Chain Validation] Failed: Ledger is empty.")
            return


    def validate(self) -> bool:
        if len(self.ledger) == 0:
            Logger.warning("[Chain Validation] Cannot validate. The ledger is empty.")
            return True

        if not self.__checkIfHashMatch():
            Logger.warning("[Chain Validation] Failed: hash mismatch detected.")
            return False

        if not self.__checkIfAllBlocksAreMined():
            Logger.warning("[Chain Validation] Failed: unmined block detected.")
            return False

        if not self.__checkChainLinkage(self.ledger):
            Logger.warning("[Chain Validation] Failed: chain linkage broken.")
            return False

        Logger.info("[Chain Validation] Chain is valid.")
        return True

    
    def __checkIfAllBlocksAreMined(self) -> bool:

        for i in self.ledger:

            hash = i["hash"]

            if hash.startswith("0000"):
                continue
            else:
                return False
        print("Validation success: All the blocks are mined.")
        return True


    def __checkIfHashMatch(self) -> bool:
        for block_dict in self.ledger:
            block = Block.model_validate(block_dict)
            recomputed = block.computeHash()  # uses stored nonce, doesn't modify it
            print(f"Computed Hash : {recomputed}")

            if block_dict["hash"] != recomputed:
                Logger.warning(
                    f"[Chain Validation] Hash mismatch on block {block_dict['index']}. "
                    f"Stored: {block_dict['hash'][:12]}... "
                    f"Computed: {recomputed[:12]}..."
                )
                return False

            Logger.info(f"[Chain Validation] Block {block_dict['index']} hash is valid.")
        return True


    def __checkChainLinkage(self, ledger: list) -> bool:
        # Genesis block must have the zero hash
        if ledger[0]["previousHash"] != "0" * 64:
            Logger.warning("[Chain Validation] Genesis block has invalid previousHash.")
            return False

        for i in range(len(ledger) - 1):
            if ledger[i + 1]["previousHash"] != ledger[i]["hash"]:
                Logger.warning(
                    f"[Chain Validation] Linkage broken between "
                    f"block {i} and block {i + 1}."
                )
                return False
        return True

