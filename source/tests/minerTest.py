from source.services.miner import Miner
from source.models.constants import TARGET


def test_mined_block_satisfies_target(unminedBlock):
    mined = Miner.mine(unminedBlock)
    assert mined.hash.startswith(TARGET)


def test_mined_block_hash_matches_compute(unminedBlock):
    mined = Miner.mine(unminedBlock)
    assert mined.hash == mined.computeHash()


def test_mining_increments_nonce(unminedBlock):
    original_nonce = unminedBlock.nonce
    mined = Miner.mine(unminedBlock)
    assert mined.nonce >= original_nonce
    assert mined.nonce > 0  # virtually guaranteed at difficulty 4


def test_mining_same_block_twice_is_deterministic(unminedBlock):
    import copy
    blockCopy = copy.deepcopy(unminedBlock)

    mined1 = Miner.mine(unminedBlock)
    mined2 = Miner.mine(blockCopy)

    assert mined1.nonce == mined2.nonce
    assert mined1.hash == mined2.hash


def test_isMined_true_after_mining(minedBlock):
    assert minedBlock.isMined() is True


def test_isMined_false_before_mining(unminedBlock):
    assert unminedBlock.isMined() is False


def test_isHashValid_true_after_mining(minedBlock):
    assert minedBlock.isHashValid() is True


def test_isHashValid_false_after_tamper(minedBlock):
    minedBlock.nonce += 1  # mutate without re-mining
    assert minedBlock.isHashValid() is False