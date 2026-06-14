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


def test_valid_chain_passes(ledgerWithTwoBlocks):
    cv = ChainValidation(ledgerWithTwoBlocks.filePath)
    assert cv.validate() is True


def test_genesis_only_chain_passes(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)

    cv = ChainValidation(ledger.filePath)
    assert cv.validate() is True


def test_tampered_block_raises_hash_mismatch(ledgerWithTwoBlocks):
    blocks = json.loads(ledgerWithTwoBlocks.filePath.read_text())
    blocks[1]["nonce"] = 999999  # tamper without re-mining
    ledgerWithTwoBlocks.filePath.write_text(json.dumps(blocks))

    cv = ChainValidation(ledgerWithTwoBlocks.filePath)
    with pytest.raises(BlockHashMismatchError):
        cv.validate()


def test_unmined_block_raises(ledgerWithTwoBlocks):
    blocks = json.loads(ledgerWithTwoBlocks.filePath.read_text())
    blocks[1]["hash"] = "ffff" + "0" * 60  # doesn't satisfy TARGET
    ledgerWithTwoBlocks.filePath.write_text(json.dumps(blocks))

    cv = ChainValidation(ledgerWithTwoBlocks.filePath)
    with pytest.raises(BlockNotMinedError):
        cv.validate()


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