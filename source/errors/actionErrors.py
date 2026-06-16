
class UnknowActionError(Exception):
    def __init__(self, action: str) -> None:
        super().__init__(f"Got an unknown action: {action}")