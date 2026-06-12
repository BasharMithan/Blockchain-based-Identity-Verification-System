
import json
from pathlib import Path

from source.models.Models import NodeMetadata, NodeConnectionType
from source.utils.logger import Logger

from source.errors import NodeStorageError



class NodeStorageManager:
    def __init__(self, nodeID: str):
        self.filePath: Path = Path(f"storage/.known-nodes-{nodeID}.json")
        # Active connections (actual P2P Node objects)
        self.nodes = []
        
        # Ensure the persistent storage file exists
        self.__initStorage()

    def __initStorage(self):
        """Initializes the JSON file if it doesn't exist."""
        if not self.filePath.is_file():
            self.__createStorageFile()

    def __createStorageFile(self) -> None:
        if not self.filePath.is_file():
            # ensure parent exists
            self.filePath.parent.mkdir(parents=True, exist_ok=True)
            # create an empty JSON array so json.load() works
            # self.filePath.write_text('[]', encoding='utf-8')

    def __loadNodes(self) -> None:
        """Loads discovered nodes from disk."""
        self.nodes = []
        try:
            with open(self.filePath, "r", encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

        if not isinstance(data, list):
            data = []

        for item in data:
            # item is a dict; use model_validate for dict inputs
            try:
                self.nodes.append(NodeMetadata.model_validate(item))
            except Exception:
                # skip invalid entries
                continue



    def __saveNodes(self, node: NodeMetadata):
        """Saves discovered nodes to disk."""
        # Read existing list (fall back to empty list on errors)
        try:
            with open(self.filePath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except OSError as error:
            raise NodeStorageError(str(self.filePath), str(error)) from error


        node_dict = node.model_dump()

        # avoid duplicate entries by nodeID if present
        node_id = node_dict.get('nodeID')
        if node_id is not None:
            if not any((d.get('nodeID') == node_id) for d in data):
                data.append(node_dict)
        else:
            data.append(node_dict)

        # ensure enums and other non-serializable types are converted
        def _default_serializer(o):
            if hasattr(o, 'value'):
                return o.value
            return str(o)

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=_default_serializer)
        except OSError as error:
            raise NodeStorageError(str(self.filePath), str(error)) from error

        # refresh in-memory list
        self.__loadNodes()


    def registerNode(self, node: NodeMetadata):
        """Adds a node address to the persistent list if it isn't already there."""

        self.__loadNodes()

        # Checking if a node is discovered. If so, we don't store it again.
        for n in self.nodes:
            if (node.host == n.host and node.port == n.port):
                Logger.info(f"[Node-storage] Node: {(node.host, node.port)} is already discovered.")
                return 

        self.__saveNodes(node)
        Logger.info(f"[Node-storage] Discovered and saved new peer: {node.host}:{node.port}")

    def get_all_discovered_nodes(self):
        """Returns a list of all known node addresses for bootstrapping."""
        return self.nodes if self.nodes else self.__loadNodes()



if __name__ == "__main__":
    storage_manager = NodeStorageManager("GG")

    for i in range(1, 10):
        storage_manager.registerNode(
            NodeMetadata(nodeID=f"{i}", host="localhost", port=888,
                         connectionType=NodeConnectionType.inbound)
                         )

    print(storage_manager.nodes)

"""
Refactor blockchain network handling and storage management;
- Enhance logging functionality.
- Changing the name of the node class from `BlockchainNetworkHandler` -> `Peer`.
- Adding duplication check logic for the ledger and the node storage.
"""

