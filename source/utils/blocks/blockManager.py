from p2pnetwork.node import Node

from source.models.Models import Block, Action
from source.services.ledger import Ledger
from source.utils.logger import Logger
from source.utils.blocks.miner import Miner
from source.utils.chain_validation import ChainValidation
from source.utils.blockValidation import BlockValidator
from source.utils.utility_function import LedgerUtilities

from source.errors import DuplicateBlockError, InvalidChainError, BlockPreviousHashError


class BlockManager:
    """Manages the block functionalities and validates if the inserted block is valid."""

    def __init__(self, ledgerInstance: Ledger, seenBlocks: set) -> None:
        # BlockManager expects a Ledger instance. The Ledger object encapsulates
        # the file path and persistence details; callers should create the
        # Ledger and pass it here.
        self.ledger = ledgerInstance
        self.miner = Miner()
        self.seenBlocks = seenBlocks
        

    def registerBlock(self, block: Block) -> Block:

        with self.ledger._lock:
            block.index = len(self.ledger.blocks)
            block.previousHash = self.ledger.getLatestHash()
        

            if self.checkIfBlockExists(block.data.chid, self.ledger.blocks):
                Logger.warning(f"[Block validation] The block {block.index} already in the ledger!")
                raise DuplicateBlockError(block.data.chid)

            minedBlock = self.miner.mine(block)

            if not self.__validChain():
                raise InvalidChainError("Chain failed integrity check before insert.")


            self.ledger.insertBlock(minedBlock)

        return minedBlock

    def receiveBlock(self, block: Block) -> Block | None:

        """
        Receives the block from the network and the API,
        checks it's validity and adds it to the chain.
        """

        if self.checkIfBlockExists(block.data.chid, self.ledger.blocks):
            raise DuplicateBlockError(block.data.chid)

        blockValidation = BlockValidator()
        try:
            blockValidation.validate(block, self.ledger.blocks[-1]["hash"])
        except BlockPreviousHashError:
            return

        self.ledger.insertBlock(block)
        Logger.info(f"[Block Validation] Received block {block.index} inserted.")
        return block




    def __validChain(self) -> bool:
        return ChainValidation(self.ledger.blocks).validate()

    @classmethod  
    def checkIfBlockExists(cls, targetCHID: str, blocks: list) -> bool:
        return any(targetCHID == b.get("data", {}).get("chid") for b in blocks)
        
    def shouldBoradcast(self, block: Block) -> bool:

        if block.data.chid in self.seenBlocks:
            return False
        else:
            self.seenBlocks.add(block.data.chid)
            return True


    """
    def broadcastBlock(self, block: Block) -> None:

        self.network.send_to_nodes(
            {
                "action": Action.BlockBroadcast.value,
                "data": block.model_dump(mode="json")
            }
        )"""