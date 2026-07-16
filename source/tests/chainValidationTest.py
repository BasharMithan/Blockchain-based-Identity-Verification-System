import json
import pytest

from source.utils.chain_validation import ChainValidation
from source.services.ledger import Ledger
from source.utils.blocks.miner import Miner
from source.models.Models import Block
from source.errors import (
    BlockHashMismatchError,
    BlockNotMinedError,
    BlockPreviousHashError,
    GenesisBlockError,
)


def test_valid_chain_passes(ledgerWithTwoBlocks: Ledger):
    cv = ChainValidation(ledgerWithTwoBlocks.blocks)
    assert cv.validate() is True


def test_genesis_only_chain_passes(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)

    cv = ChainValidation(ledger.blocks)
    assert cv.validate() is True


def test_tampered_block_raises_hash_mismatch(ledgerWithTwoBlocks: Ledger):
    blocks = ledgerWithTwoBlocks.blocks

    blocks[1]["nonce"] = 999999  # tamper without re-mining
    
    ledgerWithTwoBlocks.updateLedger(blocks)

    cv = ChainValidation(ledgerWithTwoBlocks.blocks)
    with pytest.raises(BlockHashMismatchError):
        cv.validate()


def test_unmined_block_raises(ledgerWithTwoBlocks: Ledger):
    blocks = ledgerWithTwoBlocks.blocks 
    blocks[1]["hash"] = "ffff" + "0" * 60  # doesn't satisfy TARGET
    ledgerWithTwoBlocks.updateLedger(blocks)

    cv = ChainValidation(ledgerWithTwoBlocks.blocks)
    with pytest.raises(BlockNotMinedError):
        cv.validate()


def test_broken_linkage_raises(ledgerWithTwoBlocks: Ledger):
    blocks = ledgerWithTwoBlocks.blocks

    # Re-mine block 1 with a wrong previousHash so ITS OWN hash stays valid,
    # but it no longer links to block 0's actual hash
    tampered = Block.model_validate(blocks[1])
    tampered.previousHash = "f" * 64
    remined = Miner.mine(tampered)
    blocks[1] = remined.model_dump(mode="json")

    ledgerWithTwoBlocks.updateLedger(blocks)

    cv = ChainValidation(ledgerWithTwoBlocks.blocks)
    with pytest.raises(BlockPreviousHashError):
        cv.validate()


def test_genesis_with_nonzero_previous_hash_raises(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)
    blocks = ledger.blocks

    gensisBlock = blocks[0]
    
    tampered = Block.model_validate(gensisBlock)
    tampered.previousHash = "f" * 64
    remined = Miner.mine(tampered)
    blocks[0] = remined.model_dump(mode="json")

    ledger.updateLedger(blocks)

    cv = ChainValidation(ledger.blocks)
    with pytest.raises(GenesisBlockError):
        cv.validate()