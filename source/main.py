
from services.peer import Peer


def main() -> None:
    mainPeer: Peer = Peer(title="Self", bootstrap=True, host="localhost", port=8888)
    mainPeer.startNetwork()


if __name__ == "__main__":
    main()