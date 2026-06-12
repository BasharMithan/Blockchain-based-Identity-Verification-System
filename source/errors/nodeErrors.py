

class NodeConnectionError(Exception):
    """Raised when a peer connection attempt fails."""
    def __init__(self, host: str, port: int):
        super().__init__(
            f"Failed to connect to node at {host}:{port}."
        )

class NodeStorageError(Exception):
    """Raised when a peer cannot be saved to or loaded from persistent storage."""
    def __init__(self, path: str, reason: str):
        super().__init__(
            f"Node storage error at '{path}': {reason}"
        )

class InvalidBlockPayloadError(Exception):
    """Raised when a received network payload cannot be parsed into a Block."""
    def __init__(self, reason: str):
        super().__init__(
            f"Received invalid block payload: {reason}"
        )

class UnknownActionError(Exception):
    """Raised when node_message receives an action value not in the Action enum."""
    def __init__(self, action: str):
        super().__init__(
            f"Unknown action received: '{action}'. "
            f"Expected one of: REGISTERATION, QWERY, HOLD."
        )