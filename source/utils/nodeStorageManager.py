
import json
from pathlib import Path
from p2pnetwork.nodeconnection import NodeConnection

from source.models.Models import NodeMetadata, NodeConnectionType
from source.utils.logger import Logger

from source.errors import NodeStorageError


class NodeStorageManager:
    def __init__(self, nodeName: str):
        self.nodeName = nodeName

        # Active connections (actual P2P Node objects)
        self.nodes: list[NodeMetadata] = []

        

    def update(self, connections: list, connectionType: NodeConnectionType) -> None:
        "Takes the node.nodes_inbound or the node.nodes_outbound list and writes it to the local `self.nodes` list."

        # Converting from NodeConnection to NodeMetadata
        for node in connections:
            convertedNode: NodeMetadata = self.NodeConnectionToNodeMetadata(node, cType = connectionType)

            if not self.checkExistance(NodeMetadata.model_validate(convertedNode)):
                self.nodes.append(convertedNode)
            


    def checkExistance(self, targetNode: NodeMetadata) -> bool:
        for node in self.nodes:
            if node.host == targetNode.host and node.port == targetNode.port:
                return True
        return False

    @staticmethod
    def NodeConnectionToNodeMetadata(NCObject: NodeConnection, cType: NodeConnectionType) -> NodeMetadata:
        "Takes a NodeConnection oject and converts it into a NodeMetadata object."

        host = NCObject.host
        port = NCObject.port
        nodeID = NCObject.id

        return NodeMetadata(
            name="UNKNOWN",
            host=host,
            port=port,
            nodeID=nodeID,
            connectionType=cType
        )


    @staticmethod
    def nodeLookup(connections: list[NodeMetadata], host: str, port: int) -> NodeMetadata | None:
        for node in connections:
            if host == node.host and port == node.port:
                return node
        return None