import logging as Logger

Logger.basicConfig(
    filename='storage/log.log', 
    filemode='a', # 'a' to append logs, 'w' to overwrite the file each run
    level=Logger.DEBUG, # Lowest severity level to capture
    format='%(asctime)s - %(levelname)s - %(message)s' # Human-readable format
)
