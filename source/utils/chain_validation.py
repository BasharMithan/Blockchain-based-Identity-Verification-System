

from source.utils.utility_function import LedgerUtilities
from source.utils.blockValidation import BlockValidator
from source.utils.logger import Logger
from source.models.Models import Block

from source.errors import LedgerCorruptError
from source.errors import GenesisBlockError
from source.errors import BlockPreviousHashError


class ChainValidation:
    """Validates if the chain is valid based on 3 important checks:
        1. Check if the content of a block match the hash assigned to that block,
        by recomputing the hash of these content.
        2. Check if all the blocks' hash starts with 4 zeros (Mined).
        3. Check if the hash of the N block matches the hash of the N + 1 block."""

    def __init__(self) -> None:

        Logger.info("[Chain Validation] Initializing the chain validator.")

    def validate(self) -> bool:
        ledger = LedgerUtilities.readLedger()
        blockValidator = BlockValidator()




        if len(ledger) == 0:
            Logger.warning("[Chain Validation] Cannot validate. The ledger is empty.")
            return True

        for block_dict in ledger:
            block = Block.model_validate(block_dict)

            blockValidator.validate(block)

 
        self.__checkChainLinkage(ledger)

        Logger.info("[Chain Validation] Chain is valid.")
        return True


    def __checkChainLinkage(self, ledger: list) -> bool:
        # Genesis block must have the zero hash
        if ledger[0]["previousHash"] != "0"*64:
            raise GenesisBlockError("Genesis block has invalid previousHash.")

        for i in range(len(ledger) - 1):
            if ledger[i + 1]["previousHash"] != ledger[i]["hash"]:

                raise BlockPreviousHashError(
                    index=ledger[i + 1]["index"],
                    expected=ledger[i + 1]["previousHash"],
                    got=ledger[i]["hash"]
                    )

        return True

    