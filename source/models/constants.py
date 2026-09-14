from pathlib import Path

DIFFICULTY = 4
TARGET = "0" * DIFFICULTY

BOOTSTRAP_NODES = [
    ("127.0.0.1", 8000)
]


CONFIGURATION_FILE_PATH = Path.resolve(Path("source/settings.yml"))