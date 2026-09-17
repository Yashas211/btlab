# merkle_blockchain_short.py — compact version

import hashlib
import json
import time
from typing import List, Tuple


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hstr(s: str) -> str:
    return sha256(s.encode())


class MerkleTree:

    def __init__(self, leaves: List[str]):
        self.leaves = [hstr(l) for l in leaves]
        self.levels = [self.leaves] if self.leaves else []
        self.build()

    def build(self):
        cur = self.leaves.copy()

        while len(cur) > 1:
            nxt = []

            for i in range(0, len(cur), 2):
                a = cur[i]
                b = cur[i + 1] if i + 1 < len(cur) else a

                nxt.append(
                    sha256(
                        bytes.fromhex(a) + bytes.fromhex(b)
                    )
                )

            cur = nxt
            self.levels.append(cur)

    def root(self) -> str:
        return self.levels[-1][0] if self.levels else ''

    def proof(self, idx: int) -> List[Tuple[str, str]]:

        if not (0 <= idx < len(self.leaves)):
            raise IndexError("Invalid leaf index")

        p = []
        i = idx

        for lvl in self.levels[:-1]:

            sib = i + 1 if i % 2 == 0 else i - 1

            if sib >= len(lvl):
                sib = i

            p.append(
                (
                    lvl[sib],
                    'right' if i % 2 == 0 else 'left'
                )
            )

            i //= 2

        return p

    @staticmethod
    def verify(
        leaf: str,
        proof: List[Tuple[str, str]],
        root: str
    ) -> bool:

        cur = hstr(leaf)

        for s, pos in proof:

            if pos == 'right':
                cur = sha256(
                    bytes.fromhex(cur) +
                    bytes.fromhex(s)
                )
            else:
                cur = sha256(
                    bytes.fromhex(s) +
                    bytes.fromhex(cur)
                )

        return cur == root


class Block:

    def __init__(
        self,
        idx: int,
        txs: List[str],
        prev: str,
        diff: int = 2
    ):

        self.idx = idx
        self.txs = txs[:]
        self.prev = prev
        self.diff = diff

        self.ts = time.time()
        self.nonce = 0

        self.merkle = MerkleTree(self.txs).root()
        self.hash = self._hash()

    def _hash(self) -> str:

        obj = {
            'idx': self.idx,
            'ts': self.ts,
            'prev': self.prev,
            'nonce': self.nonce,
            'merkle': self.merkle,
            'cnt': len(self.txs)
        }

        return sha256(
            json.dumps(
                obj,
                sort_keys=True
            ).encode()
        )

    def mine(self):

        target = '0' * self.diff

        while True:

            self.hash = self._hash()

            if self.hash.startswith(target):
                break

            self.nonce += 1


class Blockchain:

    def __init__(self, diff=2):

        self.diff = diff
        self.chain: List[Block] = []

        # Create genesis block
        g = Block(
            0,
            ['genesis'],
            '0' * 64,
            diff
        )

        g.mine()
        self.chain.append(g)

    def add(self, txs: List[str]) -> Block:

        b = Block(
            len(self.chain),
            txs,
            self.chain[-1].hash,
            self.diff
        )

        b.mine()
        self.chain.append(b)

        return b

    def valid(self) -> bool:

        for i in range(1, len(self.chain)):

            b = self.chain[i]
            p = self.chain[i - 1]

            # Check previous block hash
            if b.prev != p.hash:
                return False

            # Check Proof of Work
            if not b.hash.startswith(
                '0' * b.diff
            ):
                return False

            # Check Merkle Root
            if MerkleTree(b.txs).root() != b.merkle:
                return False

            # Check block hash
            if b._hash() != b.hash:
                return False

        return True


if __name__ == '__main__':

    # Create blockchain with difficulty 3
    bc = Blockchain(diff=3)

    # Add first block
    b1 = bc.add([
        "Alice->Bob:5",
        "Carol->Dave:2",
        "Eve->Frank:7"
    ])

    print(
        "Block",
        b1.idx,
        "hash",
        b1.hash,
        "merkle",
        b1.merkle
    )

    # Add second block
    b2 = bc.add([
        "Ivy->John:3",
        "Alice->Carol:1"
    ])

    print(
        "Block",
        b2.idx,
        "hash",
        b2.hash
    )

    # Validate blockchain
    print(
        "Chain valid?",
        bc.valid()
    )

    # Merkle proof example
    proof = MerkleTree(b1.txs).proof(1)

    print(
        "Proof for tx:",
        b1.txs[1]
    )

    print(proof)

    print(
        "Verify:",
        MerkleTree.verify(
            b1.txs[1],
            proof,
            b1.merkle
        )
    )
