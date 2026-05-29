from source.models.Models import User ,Identity, Response, Block, Qwery
from source.utils.generators import IDGenerator
from source.services.ledger import Ledger

class Verifier:
    def __init__(self) -> None:
        ...

    @staticmethod
    def check(qwery: Qwery) -> Response:
            ledger = Ledger()

            data: Qwery = qwery
            user, credential = data.user, data.credential
            HID = user.HID
            CID = credential.CID
            AUTHID = credential.issuer.AUTHID
            CHID = IDGenerator.generateCHID(HID=HID, CID=CID, AUTHID=AUTHID)

            if ledger.chidExists(CHID):
                return Response.appove

            return Response.decline


