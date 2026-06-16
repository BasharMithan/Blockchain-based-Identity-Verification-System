

class BlockNotMinedError(Exception):
    """Raised when a block's hash does not satisfy the proof-of-work target."""
    def __init__(self, index: int, hash: str):
        super().__init__(
            f"Block {index} is not mined. Hash '{hash[:12]}...' "
            f"does not satisfy the proof-of-work target."
        )

class BlockHashMismatchError(Exception):
    """Raised when a block's stored hash does not match a recomputation of its contents."""
    def __init__(self, index: int, stored: str, computed: str):
        super().__init__(
            f"Block {index} hash mismatch. "
            f"Stored: '{stored[:12]}...' Computed: '{computed[:12]}...'"
        )

class BlockPreviousHashError(Exception):
    """Raised when a block's previousHash does not match the current chain tip."""
    def __init__(self, index: int, expected: str, got: str):
        super().__init__(
            f"Block {index} previousHash mismatch. "
            f"Expected: '{expected[:12]}...' Got: '{got[:12]}...'"
        )

class DuplicateBlockError(Exception):
    """Raised when a block with the same CHID already exists in the ledger."""
    def __init__(self, chid: str):
        super().__init__(
            f"Block with CHID '{chid[:12]}...' already exists in the ledger."
        )


class GensisBlockHasInvalidPreviousHash(Exception):
    """Raised when the previous hash of the gensis is not 0*64"""
    def __init__(self, gensisBlockPH: str):
        super().__init__(
            f"The previous hash of the gensis block must be '{str('0'*64)[:12]}...' got {gensisBlockPH[:12]}..."

        )
        