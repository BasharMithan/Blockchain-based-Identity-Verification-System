

class LedgerNotFoundError(Exception):
    """Raised when the ledger file does not exist and cannot be created."""
    def __init__(self, path: str):
        super().__init__(
            f"Ledger file not found and could not be created at '{path}'."
        )

class LedgerCorruptError(Exception):
    """Raised when the ledger file exists but contains invalid or unparseable data."""
    def __init__(self, path: str):
        super().__init__(
            f"Ledger file at '{path}' is corrupt or contains invalid JSON."
        )

class InvalidChainError(Exception):
    """Raised when ChainValidation detects the stored chain is invalid."""
    def __init__(self, reason: str):
        super().__init__(
            f"Chain integrity check failed: {reason}"
        )

class GenesisBlockError(Exception):
    """Raised when genesis block generation or validation fails."""
    def __init__(self, reason: str):
        super().__init__(
            f"Genesis block error: {reason}"
        )