



import json
from pathlib import Path


class LedgerUtilities:

    
    path = Path(__file__).resolve().parents[2] / "storage" / ".ledger.json"


    @staticmethod
    def readLedger() -> list:
        try:
            with LedgerUtilities.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []   # corrupt file — treat as empty
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    
    @staticmethod
    def getLedgerLength() -> int:
        """Returns how many blocks are in the /storage/.ledger.json file."""
        return len(LedgerUtilities.readLedger())

    @staticmethod
    def getLatestHash() -> str:
            """
            Return the latest block's hash as a hex string.
            Falls back to 64 zeros when no blocks or an error occurs.
            Handles both dict-shaped blocks and dataclass/objects with a 'hash' attribute.
            """

            blocks = LedgerUtilities.readLedger()

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
            with open(LedgerUtilities.path, "r", encoding='utf-8') as ledgerFile:
                data = json.load(ledgerFile)
                for block in data:
                    blocks.append(block)
            return blocks[-1]
        except json.JSONDecodeError:
            return None
    
