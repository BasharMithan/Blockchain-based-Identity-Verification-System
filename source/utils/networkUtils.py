from p2pnetwork.nodeconnection import NodeConnection
from p2pnetwork.node import Node
from typing import Callable

from utils.nodeStorageManager import NodeStorageManager

from models.Models import NodeConnectionType, Payload
from models.Models import NodeMetadata

class NetworkCallbacks:

    def __init__(self, nodeManagerInstance: NodeStorageManager) -> None:
        self.nodeManager = nodeManagerInstance

    def inboundConnectionCallback(self, inboundConnections: list[NodeConnection]) -> None:
        "A callback function that gets triggered when a node makes a connection with us."
        self.nodeManager.update(inboundConnections, NodeConnectionType.inbound)


    def outboundConnectionCallback(self, outboundConnections: list[NodeConnection]) -> None:
        "A callback that gets triggered when a connection with a node was sucessful."
        self.nodeManager.update(outboundConnections, NodeConnectionType.outbound)

    def messageCallback(self, message: Payload, handler: Callable) -> None:
        """A callback function that gets triggered when the node receives a message,
           it processes that message using the callback function: `handler`."""

        handler(message)

        ...


def buildNodeInformation(name: str, node: Node) -> NodeMetadata:
    return NodeMetadata(
        name=name,
        nodeID="",
        host=node.host,
        port=node.port,
        connectionType=NodeConnectionType.inbound)