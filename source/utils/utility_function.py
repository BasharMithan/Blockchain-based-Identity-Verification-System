



import json
from pathlib import Path

def readLedger() -> list:
    """Reads the /storage/.ledger.json file and returns the latest block's hash."""
    ledger_path = Path(__file__).resolve().parents[2] / "storage" / ".ledger.json"
    try:
        with ledger_path.open("r", encoding="utf-8") as ledger_file:
            ledger_data = json.load(ledger_file)
            return ledger_data
    except json.JSONDecodeError:
        return []


def getLedgerLength() -> int:
    """Returns how many blocks are in the /storage/.ledger.json file."""
    ledger_path = Path(__file__).resolve().parents[2] / "storage" / ".ledger.json"

    with ledger_path.open("r", encoding="utf-8") as ledger_file:
        ledger_data = json.load(ledger_file)

    if not isinstance(ledger_data, dict):
        raise ValueError("Ledger file must contain a JSON object.")

    blocks = ledger_data.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("Ledger file does not contain a valid blocks list.")

    return len(blocks)


if __name__ == "__main__":
    print(readLedger())