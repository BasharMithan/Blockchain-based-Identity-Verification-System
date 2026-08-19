import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from API.router import buildRouter
from services.ledger import Ledger
from utils.blocks.blockManager import BlockManager
from models.Models import Block, NodeMetadata, NodeConnectionType, User
from errors import DuplicateBlockError, InvalidChainError


class FakePeer:
    """Stand-in for Peer with a real Ledger/BlockManager but no p2p networking,
    so the API layer can be tested in isolation."""

    def __init__(self, title: str, host: str, port: int, ledgerPath):
        self.title = title
        self.host = host
        self.port = port
        self.ledger = Ledger(filePath=ledgerPath)
        self.blockManager = BlockManager(self.ledger, set())
        self.me = NodeMetadata(
            name=title, nodeID="", host=host, port=port,
            connectionType=NodeConnectionType.outbound,
        )

    def registerBlock(self, block: Block):
        try:
            return self.blockManager.registerBlock(block)
        except (DuplicateBlockError, InvalidChainError):
            return None


@pytest.fixture
def apiClient(tmp_path):
    fakePeer = FakePeer("APITestNode", "127.0.0.1", 9999, tmp_path / ".ledger-api-test.json")
    app = FastAPI()
    app.include_router(buildRouter(fakePeer))
    return TestClient(app), fakePeer


def _registerPayload(nationalNumber, identityID, issuerID, name="Alice", issuerName="JPUF"):
    return {
        "user": {"name": name, "nationalNumber": nationalNumber, "phone": 1, "age": 30, "email": "a@x.com", "birth": "1995-01-01"},
        "credential": {"image": "", "identityID": identityID},
        "issuer": {"name": issuerName, "issuerID": issuerID},
    }


# ---------------- /register ----------------

def test_register_success_returns_201_and_mined_block(apiClient):
    client, _ = apiClient
    res = client.post("/register", json=_registerPayload(1001, 1, 10))

    assert res.status_code == 201
    body = res.json()
    assert body["index"] == 1  # genesis is index 0
    assert body["hash"].startswith("0000")
    assert body["data"]["user"]["name"] == "Alice"


def test_register_duplicate_returns_409(apiClient):
    client, _ = apiClient
    payload = _registerPayload(1002, 2, 11)

    first = client.post("/register", json=payload)
    assert first.status_code == 201

    second = client.post("/register", json=payload)
    assert second.status_code == 409


def test_register_missing_field_returns_422(apiClient):
    client, _ = apiClient
    res = client.post("/register", json={"user": {"name": "Bob"}, "credential": {}, "issuer": {}})
    assert res.status_code == 422


# ---------------- /check ----------------

def test_check_approves_registered_identity(apiClient):
    client, peer = apiClient
    client.post("/register", json=_registerPayload(2002, 2, 20, name="Carol", issuerName="GovAuth"))

    res = client.post("/check", json={
        "user": "Carol", "UserID": 2002, "credentialID": 2,
        "issuer": "GovAuth", "issuerID": 20,
    })


    assert res.status_code == 200
    assert res.json() == "APPROVED"


def test_check_declines_for_mismatched_combination(apiClient):
    """Legit user, legit credential, legit issuer — but never registered together."""
    client, _ = apiClient
    client.post("/register", json=_registerPayload(3003, 30, 300, name="Dave", issuerName="AuthX"))
    client.post("/register", json=_registerPayload(3004, 31, 301, name="Eve", issuerName="AuthY"))

    res = client.post("/check", json={
        "user": "Dave", "UserID": 3003, "credentialID": 31,  # Eve's credential
        "issuer": "AuthY", "issuerID": 301,                   # Eve's issuer
    })
    assert res.status_code == 200
    assert res.json() == "DECLINED"


def test_check_returns_error_when_identifiers_unknown(apiClient):
    client, _ = apiClient
    res = client.post("/check", json={
        "user": "Nobody", "UserID": 999999, "credentialID": 999999,
        "issuer": "Nobody", "issuerID": 999999,
    })
    assert res.status_code == 200
    assert res.json()["error"] == "User-not-found"


# ---------------- /chain ----------------

def test_chain_returns_full_ledger_including_genesis(apiClient):
    client, fakePeer = apiClient
    client.post("/register", json=_registerPayload(4004, 40, 400, name="Frank", issuerName="AuthZ"))

    res = client.get("/chain")
    assert res.status_code == 200
    body = res.json()
    assert body["sender"]["name"] == fakePeer.title
    assert len(body["chain"]) == 2  # genesis + Frank's block
    assert body["chain"][0]["index"] == 0
    assert body["chain"][1]["index"] == 1


# ---------------- /status ----------------

def test_status_reports_name_host_port_and_validity(apiClient):
    client, fakePeer = apiClient
    res = client.get("/status")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == fakePeer.title
    assert body["host"] == fakePeer.host
    assert body["port"] == fakePeer.port
    assert body["chainValidity"] is True
    assert body["blocksCount"] == 1  # just genesis so far