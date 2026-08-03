from source.models.Models import User ,Identity, Response, Block, Query
from source.utils.generators import IDGenerator
from source.utils.blocks.blockManager import BlockManager
from pathlib import Path

class Verifier:
    def __init__(self) -> None:
        ...

    @staticmethod
    def check(qwery: Query) -> Response:

        ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-Bashar.json"
        mockIssuer = {
      "name": "string",
      "businessID": 0,
      "AUTHID": "3aa6ea2377c2b75edeb3a9b0cba7e83c7c3af2891cf98eae59ce12f49835dea3"}

        data: Query = qwery
        user, credential, issuer = data.user, data.credential, data.issuer
        HID = user.HID
        CID = credential.CID
        AUTHID = issuer.AUTHID
        CHID = IDGenerator.generateCHID(HID=HID, CID=CID, AUTHID=AUTHID)



        if BlockManager.checkIfBlockExists(CHID, ledgerFilePath):
            return Response.appove
        return Response.decline


