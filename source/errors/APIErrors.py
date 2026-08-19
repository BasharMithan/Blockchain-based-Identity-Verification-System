

class APIError:
    def __init__(self, error: str, message: str) -> None:
        self.error = error
        self.message = message

    def __repr__(self) -> str:
        return {
            "error": self.error,
            "message": self.message
        }.__str__()

