
import pytest
from utils.blockValidation import BlockValidator
from errors import BlockNotMinedError, BlockHashMismatchError, BlockPreviousHashError


def test_unmined_block_raises(unminedBlock):
    with pytest.raises(BlockNotMinedError):
        BlockValidator.validate(unminedBlock)


def test_mined_block_no_previous_hash_passes(minedBlock):
    assert BlockValidator.validate(minedBlock) is True


def test_mined_block_correct_previous_hash_passes(minedBlock):
    assert BlockValidator.validate(minedBlock, minedBlock.previousHash) is True


def test_mined_block_wrong_previous_hash_raises(minedBlock):
    with pytest.raises(BlockPreviousHashError):
        BlockValidator.validate(minedBlock, "wrong" * 13)


def test_tampered_block_raises_hash_mismatch(minedBlock):
    minedBlock.index = 999  # mutate after mining, hash no longer matches
    with pytest.raises(BlockHashMismatchError):
        BlockValidator.validate(minedBlock)