import json
import pytest

from source.services.ledger import Ledger
from source.services.miner import Miner
from source.errors import LedgerCorruptError, InvalidChainError, BlockHashMismatchError


def test_fresh_ledger_has_genesis(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)

    assert len(ledger.blocks) == 1
    assert ledger.blocks[0]["index"] == 0
    assert ledger.blocks[0]["previousHash"] == "0" * 64


def test_genesis_is_mined_and_hash_valid(tempLedgerPath):
    ledger = Ledger(filePath=tempLedgerPath)

    from source.models.Models import Block
    genesis = Block.model_validate(ledger.blocks[0])

    assert genesis.isMined() is True
    assert genesis.isHashValid() is True


def test_insert_persists_to_disk(ledgerWithTwoBlocks):
    # ledgerWithTwoBlocks fixture already inserted a second block
    onDisk = json.loads(ledgerWithTwoBlocks.filePath.read_text())
    assert len(onDisk) == 2
    assert onDisk[0]["index"] == 0
    assert onDisk[1]["index"] == 1


def test_reload_from_disk_matches_in_memory(ledgerWithTwoBlocks):
    reloaded = Ledger(filePath=ledgerWithTwoBlocks.filePath)

    assert len(reloaded.blocks) == len(ledgerWithTwoBlocks.blocks)
    assert reloaded.blocks[-1]["hash"] == ledgerWithTwoBlocks.blocks[-1]["hash"]


def test_insert_on_invalid_chain_raises(ledgerWithTwoBlocks, unminedBlock):
    # Corrupt the existing chain on disk before inserting a new block
    blocks = json.loads(ledgerWithTwoBlocks.filePath.read_text())
    blocks[0]["nonce"] = 999999  # breaks block 0's hash validity
    ledgerWithTwoBlocks.filePath.write_text(json.dumps(blocks))

    unminedBlock.index = 2
    unminedBlock.previousHash = blocks[-1]["hash"]
    mined = Miner.mine(unminedBlock)

    with pytest.raises(BlockHashMismatchError):
        ledgerWithTwoBlocks.insertBlock(mined)


def test_corrupt_ledger_file_raises_on_load(tempLedgerPath):
    # Write a bare JSON object instead of a list
    tempLedgerPath.write_text(json.dumps({"not": "a list"}))

    with pytest.raises(LedgerCorruptError):
        Ledger(filePath=tempLedgerPath)


def test_malformed_json_raises_on_load(tempLedgerPath):
    tempLedgerPath.write_text("{not valid json")

    with pytest.raises(LedgerCorruptError):
        Ledger(filePath=tempLedgerPath)


def test_all_blocks_returns_full_chain(ledgerWithTwoBlocks):
    all_blocks = ledgerWithTwoBlocks.allBlocks()

    assert len(all_blocks) == 2
    assert all_blocks is ledgerWithTwoBlocks.blocks  # same list reference