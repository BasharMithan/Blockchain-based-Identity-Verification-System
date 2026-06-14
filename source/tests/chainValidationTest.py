import json
import pytest

from source.utils.chain_validation import ChainValidation
from source.services.ledger import Ledger
from source.services.miner import Miner
from source.models.Models import Block          
from source.errors import (
    BlockHashMismatchError,
    BlockNotMinedError,
    BlockPreviousHashError,
    GenesisBlockError,
)


def test_broken_linkage_raises(ledgerWithTwoBlocks):
    blocks = json.loads(ledgerWithTwoBlocks.filePath.read_text())

    # Re-mine block 1 with a wrong previousHash so ITS OWN hash stays valid,
    # but it no longer links to block 0's actual hash
    tampered = Block.model_validate(blocks[1])
    tampered.previousHash = "f" * 64
    remined = Miner.mine(tampered)
    blocks[1] = json.loads(Block.model_dump_json(remined))

    ledgerWithTwoBlocks.filePath.write_text(json.dumps(blocks))

    cv = ChainValidation(ledgerWithTwoBlocks.filePath)
    with pytest.raises(BlockPreviousHashError):
        cv.validate()


def test_genesis_with_nonzero_previous_hash_raises(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)
    blocks = json.loads(ledger.filePath.read_text())

    tampered = Block.model_validate(blocks[0])
    tampered.previousHash = "f" * 64
    remined = Miner.mine(tampered)
    blocks[0] = json.loads(Block.model_dump_json(remined))

    ledger.filePath.write_text(json.dumps(blocks))

    cv = ChainValidation(ledger.filePath)
    with pytest.raises(GenesisBlockError):
        cv.validate()