import pytest

from source.services.blockManager import BlockManager
from source.services.ledger import Ledger
from source.errors import DuplicateBlockError, BlockPreviousHashError


@pytest.fixture
def blockManager(tempLedgerPath):
    return BlockManager(Ledger(filePath=tempLedgerPath))


def test_register_assigns_correct_index(blockManager, unminedBlock):
    result = blockManager.registerBlock(unminedBlock)

    # genesis is index 0, this is the first registered block
    assert result.index == 1


def test_register_assigns_correct_previous_hash(blockManager, unminedBlock):
    genesisHash = blockManager.ledger.blocks[0]["hash"]

    result = blockManager.registerBlock(unminedBlock)

    assert result.previousHash == genesisHash


def test_register_returns_mined_block(blockManager, unminedBlock):
    result = blockManager.registerBlock(unminedBlock)

    assert result.isMined() is True
    assert result.isHashValid() is True


def test_register_persists_to_ledger(blockManager, unminedBlock):
    blockManager.registerBlock(unminedBlock)

    assert len(blockManager.ledger.blocks) == 2  # genesis + new block


def test_register_duplicate_raises(blockManager, unminedBlock):
    blockManager.registerBlock(unminedBlock)

    # Build a second block with the same underlying CHID
    import copy
    duplicate = copy.deepcopy(unminedBlock)
    duplicate.nonce = 0
    duplicate.hash = ""

    with pytest.raises(DuplicateBlockError):
        blockManager.registerBlock(duplicate)

    # Ledger should still only have genesis + the first block
    assert len(blockManager.ledger.blocks) == 2


def test_receive_block_with_correct_previous_hash_stores_unchanged(blockManager, unminedBlock):
    # Simulate another node mining this block independently
    from source.services.miner import Miner

    unminedBlock.index = 1
    unminedBlock.previousHash = blockManager.ledger.blocks[0]["hash"]
    minedElsewhere = Miner.mine(unminedBlock)

    originalNonce = minedElsewhere.nonce
    originalHash = minedElsewhere.hash

    received = blockManager.receiveBlock(minedElsewhere)

    assert received.nonce == originalNonce
    assert received.hash == originalHash
    assert len(blockManager.ledger.blocks) == 2


def test_receive_block_with_wrong_previous_hash_raises(blockManager, unminedBlock):
    from source.services.miner import Miner

    unminedBlock.index = 1
    unminedBlock.previousHash = "f" * 64  # wrong — doesn't match genesis hash
    badBlock = Miner.mine(unminedBlock)

    with pytest.raises(BlockPreviousHashError):
        blockManager.receiveBlock(badBlock)

    # Ledger should remain at genesis only
    assert len(blockManager.ledger.blocks) == 1


def test_receive_duplicate_block_raises(blockManager, unminedBlock):
    from source.services.miner import Miner
    import copy

    unminedBlock.index = 1
    unminedBlock.previousHash = blockManager.ledger.blocks[0]["hash"]
    mined = Miner.mine(unminedBlock)

    blockManager.receiveBlock(mined)

    duplicate = copy.deepcopy(mined)
    with pytest.raises(DuplicateBlockError):
        blockManager.receiveBlock(duplicate)


def test_concurrent_receive_block_does_not_duplicate_same_chid(blockManager, unminedBlock, monkeypatch):
    import copy
    import threading
    from source.services.miner import Miner

    unminedBlock.index = 1
    unminedBlock.previousHash = blockManager.ledger.blocks[0]["hash"]
    mined = Miner.mine(unminedBlock)

    barrier = threading.Barrier(2)
    original_check = BlockManager.checkIfBlockExists

    def delayed_check(targetCHID, filePath):
        barrier.wait(timeout=5)
        return original_check(targetCHID, filePath)

    monkeypatch.setattr(BlockManager, "checkIfBlockExists", staticmethod(delayed_check))

    results = []
    errors = []

    def worker():
        try:
            blockManager.receiveBlock(copy.deepcopy(mined))
            results.append("ok")
        except Exception as exc:  # pragma: no cover - assertion path
            errors.append(type(exc).__name__)

    first = threading.Thread(target=worker)
    second = threading.Thread(target=worker)
    first.start()
    second.start()
    first.join()
    second.join()

    assert len(errors) == 1
    assert len(blockManager.ledger.blocks) == 2