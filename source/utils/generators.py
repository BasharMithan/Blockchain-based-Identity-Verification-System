import hashlib

class IDGenerator:
    """A helper class that contains the functions that act as a generator"""

    @staticmethod
    def generateID(entity: int | str) -> str:
            generatorInstance = IDGenerator()
            return  generatorInstance.__getHash(entity)


    @staticmethod
    def generateCHID(HID: str, CID: str, AUTHID: str) -> str:
        generatorInstance = IDGenerator()
        CHID = generatorInstance.__getHash(f"{HID}:{CID}:{AUTHID}")
        return CHID


    
    def __getHash(self, value: str | int) -> str:
        if isinstance(value, str):
            return hashlib.sha256(value.encode('utf-8')).hexdigest()

        elif isinstance(value, int):
             return hashlib.sha256(str(value).encode("utf-8")).hexdigest()