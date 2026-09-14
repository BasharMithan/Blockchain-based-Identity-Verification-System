from services.peer import Peer
from configs import settings



def main() -> None:
    Blockchain = Peer("Blockchain", "localhost", 8000)
    Blockchain.startNetwork()



if __name__ == "__main__":
    main()