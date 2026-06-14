



import json
from pathlib import Path

from source.models.constants import LEDGER_PATH


class LedgerUtilities:
    def __init__(self, filePath: Path = LEDGER_PATH) -> None:
        self.filePath: Path = filePath

    


    @staticmethod
    def readLedger(filePath: Path | None = None) -> list:
        path = filePath or LEDGER_PATH 
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []   # corrupt file — treat as empty
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    
    @staticmethod
    def getLedgerLength(filePath: Path = LEDGER_PATH) -> int:
        """Returns how many blocks are in the /storage/.ledger.json file."""
        return len(LedgerUtilities.readLedger(filePath))

    @staticmethod
    def getLatestHash(filePath: Path = LEDGER_PATH) -> str:
            """
            Return the latest block's hash as a hex string.
            Falls back to 64 zeros when no blocks or an error occurs.
            Handles both dict-shaped blocks and dataclass/objects with a 'hash' attribute.
            """

            blocks = LedgerUtilities.readLedger(filePath)

            zero_hash = "0" * 64
            try:
                # Prefer in-memory ledger
                if blocks:
                    latest = blocks[-1]
                else:
                    latest = LedgerUtilities.getLatestBlock()
                    if not latest:
                        return zero_hash
                if isinstance(latest, dict):
                    return latest.get("hash", zero_hash)
                return getattr(latest, "hash", zero_hash)
            except Exception:
                return zero_hash
        
    @staticmethod
    def getLatestBlock():
        # TODO: Move this utility function to the utils/utility_functions.py
        blocks: list = []
        try:
            with open(LEDGER_PATH, "r", encoding='utf-8') as ledgerFile:
                data = json.load(ledgerFile)
                for block in data:
                    blocks.append(block)
            return blocks[-1]
        except json.JSONDecodeError:
            return None
    
