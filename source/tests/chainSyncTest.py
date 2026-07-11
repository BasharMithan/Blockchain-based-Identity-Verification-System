import json
from pathlib import Path

import pytest

from source.models.Models import (
    Action,
    Authority,
    Block,
    CHID,
    ChainSyncRequest,
    ChainSyncResponse,
    Identity,
    NodeConnectionType,
    NodeMetadata,
    User,
)
from source.services.chainSync import ChainSync
from source.services.ledger import Ledger
from source.services.miner import Miner
from source.utils.nodeStorageManager import NodeStorageManager


class FakeNodeConnection:
    def __init__(self, host: str, port: int, node_id: str):
        self.host = host
        self.port = port
        self.id = node_id

    def __eq__(self, other):
        if not isinstance(other, FakeNodeConnection):
            return False
        return self.host == other.host and int(self.port) == int(other.port)

    def __repr__(self):
        return f"FakeNodeConnection(host={self.host}, port={self.port}, id={self.id})"


class FakeNetwork:
    def __init__(self, all_nodes=None):
        self.all_nodes = all_nodes or []
        self.sent_to_nodes = []
        self.sent_to_node = []

    def send_to_nodes(self, payload, exclude=None):
        self.sent_to_nodes.append((payload, exclude))

    def send_to_node(self, node, payload):
        self.sent_to_node.append((node, payload))


@pytest.fixture
def ledger_with_one_block(tmp_path):
    ledger_path = tmp_path / ".ledger-sync-test.json"
    ledger = Ledger(filePath=ledger_path)

    user = User(name="SyncUser1", nationalNumber=111, phone=1, age=20, email="", birth="")
    auth = Authority(name="SyncAuthority", businessID=1)
    identity = Identity(user=user, issuer=auth, image="", credentialID=1)
    chid = CHID(user=user, credential=identity, issuer=auth)
    block = Block(data=chid)
    block.index = len(ledger.blocks)
    block.previousHash = ledger.blocks[-1]["hash"]
    mined = Miner.mine(block)
    ledger.insertBlock(mined)

    return ledger


@pytest.fixture
def ledger_with_two_blocks(tmp_path):
    ledger = Ledger(filePath=tmp_path / ".ledger-sync-test.json")

    for idx in range(2):
        user = User(name=f"SyncUser_{idx}", nationalNumber=100 + idx, phone=idx, age=20, email="", birth="")
        auth = Authority(name="SyncAuthority", businessID=idx)
        identity = Identity(user=user, issuer=auth, image="", credentialID=idx)
        chid = CHID(user=user, credential=identity, issuer=auth)
        block = Block(data=chid)
        block.index = len(ledger.blocks)
        block.previousHash = ledger.blocks[-1]["hash"]
        mined = Miner.mine(block)
        ledger.insertBlock(mined)

    return ledger


def test_request_sends_chain_sync_request_to_known_nodes(tmp_path):
    network = FakeNetwork()
    self_conn = FakeNodeConnection(host="127.0.0.1", port=5001, node_id="self")
    peer_conn = FakeNodeConnection(host="127.0.0.1", port=5002, node_id="peer")
    network.all_nodes = [self_conn, peer_conn]

    self_meta = NodeMetadata(
        name="SelfNode",
        nodeID="self",
        host="127.0.0.1",
        port=5001,
        connectionType=NodeConnectionType.outbound,
    )

    chain_sync = ChainSync(
        ledger=Ledger(filePath=tmp_path / ".ledger-sync-request.json"),
        network=network,
        receivedLedgers=[],
        receivedLengths=[],
        me=self_meta,
    )

    chain_sync.request()

    assert chain_sync.expectedResponses == len(network.all_nodes)
    assert len(network.sent_to_nodes) == 1
    payload, exclude = network.sent_to_nodes[0]
    assert payload["action"] == Action.chainSyncRequest.value
    assert isinstance(payload["data"], dict)
    assert exclude == [self_conn]


def test_send_responds_with_local_ledger_when_valid(tmp_path):
    self_conn = FakeNodeConnection(host="127.0.0.1", port=5001, node_id="self")
    peer_conn = FakeNodeConnection(host="127.0.0.1", port=5002, node_id="peer")

    network = FakeNetwork(all_nodes=[self_conn, peer_conn])
    self_meta = NodeMetadata(
        name="SelfNode",
        nodeID="self",
        host="127.0.0.1",
        port=5001,
        connectionType=NodeConnectionType.outbound,
    )
    peer_meta = NodeMetadata(
        name="PeerNode",
        nodeID="peer",
        host="127.0.0.1",
        port=5002,
        connectionType=NodeConnectionType.outbound,
    )

    ledger = Ledger(filePath=tmp_path / ".ledger-send.json")
    chain_sync = ChainSync(
        ledger=ledger,
        network=network,
        receivedLedgers=[],
        receivedLengths=[],
        me=self_meta,
    )

    request = ChainSyncRequest(sender=peer_meta)
    chain_sync.send(request)

    assert len(network.sent_to_node) == 1
    target_node, payload = network.sent_to_node[0]
    assert target_node is peer_conn
    assert payload["action"] == Action.chainSyncResponse.value
    assert payload["data"]["length"] == len(ledger.blocks)


def test_send_skips_send_when_local_ledger_invalid(tmp_path, monkeypatch):
    self_conn = FakeNodeConnection(host="127.0.0.1", port=5001, node_id="self")
    peer_conn = FakeNodeConnection(host="127.0.0.1", port=5002, node_id="peer")

    network = FakeNetwork(all_nodes=[self_conn, peer_conn])
    self_meta = NodeMetadata(
        name="SelfNode",
        nodeID="self",
        host="127.0.0.1",
        port=5001,
        connectionType=NodeConnectionType.outbound,
    )
    peer_meta = NodeMetadata(
        name="PeerNode",
        nodeID="peer",
        host="127.0.0.1",
        port=5002,
        connectionType=NodeConnectionType.outbound,
    )

    ledger = Ledger(filePath=tmp_path / ".ledger-send-invalid.json")
    chain_sync = ChainSync(
        ledger=ledger,
        network=network,
        receivedLedgers=[],
        receivedLengths=[],
        me=self_meta,
    )

    monkeypatch.setattr(chain_sync, "validateBeforeSending", lambda ledger: False)
    chain_sync.send(ChainSyncRequest(sender=peer_meta))

    assert len(network.sent_to_node) == 0


def test_receive_updates_ledger_with_longer_valid_chain(tmp_path):
    local = Ledger(filePath=tmp_path / ".ledger-local.json")
    remote = Ledger(filePath=tmp_path / ".ledger-remote.json")

    for idx in range(2):
        user = User(name=f"RemoteUser_{idx}", nationalNumber=300 + idx, phone=idx, age=25, email="", birth="")
        auth = Authority(name="RemoteAuth", businessID=10 + idx)
        identity = Identity(user=user, issuer=auth, image="", credentialID=idx)
        chid = CHID(user=user, credential=identity, issuer=auth)
        block = Block(data=chid)
        block.index = len(remote.blocks)
        block.previousHash = remote.blocks[-1]["hash"]
        remote.insertBlock(Miner.mine(block))

    # Remote chain is longer than local chain
    assert len(remote.blocks) > len(local.blocks)

    network = FakeNetwork()
    self_meta = NodeMetadata(
        name="SelfNode",
        nodeID="self",
        host="127.0.0.1",
        port=5001,
        connectionType=NodeConnectionType.outbound,
    )
    chain_sync = ChainSync(
        ledger=local,
        network=network,
        receivedLedgers=[],
        receivedLengths=[],
        me=self_meta,
    )
    chain_sync.expectedResponses = 1

    response = ChainSyncResponse(sender=self_meta, ledger=remote.blocks, length=len(remote.blocks))
    chain_sync.receive(response)

    assert len(local.blocks) == len(remote.blocks)
    assert local.blocks == remote.blocks


def test_receive_does_not_replace_with_shorter_chain(tmp_path):
    local = Ledger(filePath=tmp_path / ".ledger-local-short.json")
    for idx in range(2):
        user = User(name=f"LocalUser_{idx}", nationalNumber=400 + idx, phone=idx, age=25, email="", birth="")
        auth = Authority(name="LocalAuth", businessID=20 + idx)
        identity = Identity(user=user, issuer=auth, image="", credentialID=idx)
        chid = CHID(user=user, credential=identity, issuer=auth)
        block = Block(data=chid)
        block.index = len(local.blocks)
        block.previousHash = local.blocks[-1]["hash"]
        local.insertBlock(Miner.mine(block))

    remote = Ledger(filePath=tmp_path / ".ledger-remote-short.json")
    assert len(remote.blocks) < len(local.blocks)

    network = FakeNetwork()
    self_meta = NodeMetadata(
        name="SelfNode",
        nodeID="self",
        host="127.0.0.1",
        port=5001,
        connectionType=NodeConnectionType.outbound,
    )
    chain_sync = ChainSync(
        ledger=local,
        network=network,
        receivedLedgers=[],
        receivedLengths=[],
        me=self_meta,
    )
    chain_sync.expectedResponses = 1

    response = ChainSyncResponse(sender=self_meta, ledger=remote.blocks, length=len(remote.blocks))
    chain_sync.receive(response)

    assert len(local.blocks) != len(remote.blocks)
    assert local.blocks != remote.blocks
