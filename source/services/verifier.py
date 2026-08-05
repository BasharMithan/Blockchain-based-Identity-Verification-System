from source.models.Models import Response, Query
from source.utils.generators import IDGenerator
from source.utils.blocks.blockManager import BlockManager
from pathlib import Path


class Verifier:

    @staticmethod
    def check(qwery: Query) -> Response:

        ledgerFilePath = Path(__file__).resolve().parents[2] / "storage" / f".ledger-Bashar.json"

        data: Query = qwery
        user, credential, issuer = data.user, data.credential, data.issuer
        HID = user.HID
        CID = credential.CID
        AUTHID = issuer.AUTHID
        CHID = IDGenerator.generateCHID(HID=HID, CID=CID, AUTHID=AUTHID)



        if BlockManager.checkIfBlockExists(CHID, ledgerFilePath):
            return Response.appove
        return Response.decline


