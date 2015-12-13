# Store a collection of meshes
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import pymel.core as pmc
import collections

class Meshes(collections.MutableSet):
    """ Container for storing meshes """
    def __init__(s, name):
        s.nodes = pmc.ls(name, r=True, type="objectSet") or [pmc.sets(n=name)]
    def add(s, m): s.nodes[0].add(m)
    def discard(s, m):
        for sel in s.nodes:
            if m in sel: sel.remove(m)
    def __len__(s): return sum(len(a) for a in s.nodes)
    def __iter__(s):
        no_repeat = set()
        for n in s.nodes:
            for m in n:
                if m not in no_repeat:
                    no_repeat.add(m)
                    yield m
    def __contains__(s, m): return m in set(a for a in s)
    def __repr__(s): return "Collection :: %s" % repr(set(a for a in s))

if __name__ == '__main__':
    # Testing
    import random
    def rand_pos(): return [random.random() * 10 - 5 for a in range(3)]
    pmc.system.newFile(force=True)
    objs = [pmc.polySphere()[0] for a in range(5)]
    for o in objs: pmc.xform(o, t=rand_pos())
    name = "OutOfControlRig"

    set1 = pmc.sets(objs[:2], n="some:thing:%s" % name)

    container = Meshes("OutOfControlRig")
    print "contains".center(20, "-")
    print container
    print "added".center(20, "-")
    for o in objs: container.add(o)
    print container
