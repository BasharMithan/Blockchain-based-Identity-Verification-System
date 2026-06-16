from source.models.Models import Block
from source.utils.logger import Logger
from source.errors import BlockNotMinedError, BlockHashMismatchError, BlockPreviousHashError

class BlockValidator:

    @staticmethod
    def validate(block: Block, previousHash: str | None = None) ->  bool:
        Logger.info(f"[Block Validation] Validatiing the block {block.index}.")
        """
        Validates an incoming block before insertion.
        Returns True on success or False on failure.
        """


        # 1. Proof-of-work — was this block actually mined?
        if not block.isMined():
            Logger.warning(f"[Block Validation] The block {block.index} is nor mined !")
            raise BlockNotMinedError(block.index, block.hash)

        # 2. Hash integrity — does the stored hash match a recomputation?
        if not block.isHashValid():
            Logger.warning(f"[Block Validation] The block {block.index} is modified !")
            raise BlockHashMismatchError(block.index, block.hash, block.computeHash())

        # 3. Previous hash chekcing - does the current block's PH == the hash of the previous hash?
        if previousHash is not None:
            if block.previousHash != previousHash:
                print(f"Got as PH: {previousHash}")
                Logger.warning(f"[Block Validation] The block {block.index} has an invalid previous hash !, expected: {previousHash[:12]}, got: {block.previousHash[:12]}")
                raise BlockPreviousHashError(block.index, previousHash, block.previousHash)

        Logger.info(f"[Block Validation] The block {block.index} is valid.")
        return True