from source.models.Models import CHID, User, Authority, Identity, Block
from source.utils.ledger import Ledger
from source.utils.ledger import Ledger

if __name__ == "__main__":
    user = User("Bashar", 2312311, 444, 24, "", "")
    issuer = Authority("JPU", 3423)
    doc = Identity(user, issuer, "", 333)
    chid = CHID(user=user, credential=doc, issuer=issuer)
    block = Block(0, chid, 0)

    user1 = User("Bilal", 2312311, 544, 24, "", "")
    issuer1 = Authority("JPU", 3423)
    doc1 = Identity(user1, issuer1, "", 333)
    chid1 = CHID(user=user1, credential=doc1, issuer=issuer1)
    block1 = Block(1, chid1)


ledger = Ledger()

ledger.insertBlock(block) # type: ignore
# Inserting 10 blocks
for i in range(10):
    user = User(f"User{i}", 1000000 + i, 500000 + i, 20 + (i % 30), f"user{i}@example.com", "")
    issuer = Authority(f"Issuer{i}", 2000 + i)
    doc = Identity(user, issuer, f"image{i}.png", 3000 + i)
    chid = CHID(user=user, credential=doc, issuer=issuer)
    block = Block(i, chid)
    ledger.insertBlock(block)

print(f"Total blocks in ledger: {len(ledger.allBlocks())}")