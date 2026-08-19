import time
from services.peer import Peer
from models import User

def main() -> None:
    Blockchain = Peer("Blockchain", "localhost", 8000)

    Blockchain.startNetwork()


if __name__ == "__main__":
    main()