#!/usr/bin/env python3

"""
Finite State Entropy (FSE) is an entropy coder which combines the speed of Huffman coding
(which is suboptimal) with the compression ratio of arithmetic coding (which is slow). It is used
in an optimized form within powerful compression schemes such as zstd and LZFSE.

* https://en.wikipedia.org/wiki/Finite_State_Entropy
* https://arxiv.org/abs/1311.2540
"""

from bisect import bisect_right
from collections import Counter, OrderedDict


class FSECoder(object):
    """Implements Finite State Entropy coding."""
    def __init__(self, probs):
        self.stats = Statistics(probs)

    def encode(self, symbs):
        """Encodes the given symbols via FSE coding."""
        enc = 0
        for symb in symbs:
            stats = self.stats[symb]
            div, mod = divmod(enc, stats['prob'])
            enc = self.stats.total*div + mod + stats['cdf']
        return enc

    def decode(self, enc):
        """Decodes encoded output via FSE coding."""
        symbs = []
        while enc > 0:
            div, mod = divmod(enc, self.stats.total)
            stats = self.stats.get_by_cdf(mod)
            enc = stats['prob']*div + mod - stats['cdf']
            symbs.insert(0, stats['symb'])
        return symbs


class Statistics(OrderedDict):
    """Map symbols to probability and CDF."""
    def __init__(self, prob_dict):
        super().__init__()
        self.total = 1
        for (symb, prob) in prob_dict.items():
            self[symb] = {
                'symb': symb,
                'prob': prob,
                'cdf': self.total,
            }
            self.total += prob

    def get_by_cdf(self, cdf):
        """Return the last symbol stat whose CDF is less than or equal to the given CDF."""
        values = list(self.values())
        idx = bisect_right([obj['cdf'] for obj in values], cdf)
        if not idx:
            raise ValueError("invalid cdf: " + str(cdf))
        return values[idx-1]


def naive_probs(symbs):
    """
    Naive symbol probability counter.
    Improve compression by counting groups of symbols.
    See also:
    * https://en.wikipedia.org/wiki/Dictionary_coder
    * https://en.wikipedia.org/wiki/LZ77_and_LZ78
    """
    return Counter(symbs)


if __name__ == '__main__':
    print("Testing...")

    TESTS = [
        "Hello, world!",

        "Huffman coding is limited to 1 bit per symbol. FSE can a symbol as a fraction of a bit.",

        ' '.join("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
        ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
        ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
        sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
        est laborum.
        """.split()),
    ]

    for t in TESTS:
        print("Test:", t)
        coder = FSECoder(naive_probs(t))
        encoded = coder.encode(t)
        print("  Encoded:", encoded)
        decoded = ''.join(coder.decode(encoded))
        print("  Decoded:", decoded)
        if decoded != t:
            raise ValueError("decoding failed")

    print("Tests pass.")
