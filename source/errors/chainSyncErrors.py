from models.Models import ChainSyncRequest


class ReceivedChainIsInvalid(Exception):
    def __init__(self):
        return super().__init__(f"Received chain is not valid.")





