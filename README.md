# FSE, made easy
Finite State Entropy (FSE) is an entropy coder which combines the speed of Huffman coding
(which is suboptimal) with the compression ratio of arithmetic coding (which is slow). It is used
in an optimized form within powerful compression schemes such as zstd and LZFSE.

* https://en.wikipedia.org/wiki/Finite_State_Entropy
* https://arxiv.org/abs/1311.2540

Abridged [fse.py](https://github.com/dbkaplun/fse-made-easy/blob/master/fse.py):
```py
def encode(stats, symbs):
    enc = 0
    for symb in symbs:
        s = stats[symb]
        div, mod = divmod(enc, s['prob'])
        enc = stats.total*div + mod + s['cdf']
    return enc

def decode(stats, enc):
    symbs = []
    while enc > 0:
        div, mod = divmod(enc, stats.total)
        s = stats.get_by_cdf(mod)
        enc = s['prob']*div + mod - s['cdf']
        symbs.insert(0, s['symb'])
    return symbs
```
