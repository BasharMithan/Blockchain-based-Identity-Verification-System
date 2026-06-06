from source.models.Models import Block
from source.utils.logger import Logger

class BlockValidator:

    @staticmethod
    def validate(block: Block) ->  bool:
        Logger.info(f"[Block Validation] Validatiing the block {block.index}.")
        """
        Validates an incoming block before insertion.
        Returns True on success or False on failure.
        """


        # 1. Proof-of-work — was this block actually mined?
        if not block.isMined():
            Logger.warning(f"[Block Validation] The block {block.index} is nor mined !")
            return False

        # 2. Hash integrity — does the stored hash match a recomputation?
        if not block.isHashValid():
            Logger.warning(f"[Block Validation] The block {block.index} is modified !")
            return False

        Logger.info(f"[Block Validation] The block {block.index} is valid.")
        return True