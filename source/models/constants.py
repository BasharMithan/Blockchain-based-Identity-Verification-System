from pathlib import Path

DIFFICULTY = 4
TARGET = "0" * DIFFICULTY
LEDGER_PATH = Path(__file__).resolve().parents[2] / "storage" / ".ledger.json"