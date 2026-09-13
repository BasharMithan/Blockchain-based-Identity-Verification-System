from pathlib import Path

import logging as Logger

# Encure that the storage folder exists
storageFolder = Path("storage")
storageFolder.mkdir(exist_ok=True)


Logger.basicConfig(
    filename=str(Path(__file__).resolve().parents[2] / 'storage' / 'log.log'), 

    filemode='a', # 'a' to append logs, 'w' to overwrite the file each run
    level=Logger.DEBUG, # Lowest severity level to capture
    format='%(asctime)s - %(levelname)s - %(message)s' # Human-readable format
)
