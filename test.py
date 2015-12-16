# Testing things

import timeit
import random
import sys

def build():
    for i in range(1000):
        yield (i, random.random())

d = dict(build()) # numerical index
l = list(a[1] for a in build()) # Regular index
t = tuple(a[1] for a in build())

print sorted(d)
