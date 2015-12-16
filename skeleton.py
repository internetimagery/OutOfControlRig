# Skeleton stuff

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

import maya.api.OpenMaya as om
import pymel.core as pmc
import collections
import itertools

def chunk(iterable, size):
    """ Iterate in chunks """
    iterables = itertools.tee(iterable, size)
    for a, b in enumerate(iterables):
        for c in range(a): b.next() # Offset iterables
    return itertools.izip(*iterables)

def get_ik(jnt):
    """ Get any IK handles attached to joint, if one exists """
    ik_handles = [set(e.connections(s=False, type="ikHandle")).pop() for e in set(jnt.connections(s=False, type="ikEffector"))]
    return ik_handles

def get_limb(joint):
    """ Given a joint. Walk the limb """
    roots = [joint]
    for parent in joint.getAllParents(): # Walk backwards
        if parent.type() != "joint" or len(parent.getChildren(type="joint")) != 1 : break
        roots.append(parent)
    for root in reversed(roots):
        yield root
    children = joint.getChildren(type="joint")
    while len(children) == 1: # Walk forwards
        joint = children[0]
        children = joint.getChildren(type="joint")
        yield joint

def get_twists(limb):
    """ Given a limb, return all twist joint roots """
    limb_gen = ((a, a.getTranslation("world")) for a in limb)
    try:
        for i, ((j1,j1_pos),(j2,j2_pos),(j3,j3_pos)) in enumerate(chunk(limb_gen, 3)):
            if not i: # First joint
                buff = j1 # Initialize our buffer
                yield (j1, j1) # Joint and its "root"
            vec1 = j2_pos - j1_pos
            vec2 = j3_pos - j2_pos
            if not vec1.isParallel(vec2): # We have a kink in the joint, not a twist
                buff = j2
            yield (j2, buff)
        yield (j3, j3) # End joint can't be a twist
    except StopIteration: # Joint chain is less than three, no twists
        for jnt in limb_gen:
            yield (jnt, jnt)

def get_skeleton(joints):
    """ Given a number of joints, form the corresponding limbs """
    seen = set() # Avoid duplicates
    for jnt in joints:
        if jnt not in seen:
            limb = collections.OrderedDict(get_twists(get_limb(jnt)))
            seen |= set(limb)
            yield limb

class Bones(object):
    """ Skeleton. Contains limbs. Collection of Joints """
    def __init__(s, joints):
        s.limbs = tuple(get_skeleton(joints))

    def __len__(s):
        """ Number of joints in skeleton """
        return sum(len(a) for a in s.limbs)

    def __contains__(s, joint):
        """ Confirm joint is in skeleton """
        for limb in s.limbs:
            if joint in limb: return True
        return False

    def __repr__(s):
        """ Print off skeleton contents """
        res = "Skeleton:\n"
        res += "\n".join("Limb: %s" % a for a in s.limbs)
        return res

    def get_real_joint(s, joint):
        """ Given a joint name, get corresponding non-twist joint """
        for limb in s.limbs:
            if joint in limb: return limb[joint]


if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    jnts = [pmc.joint(p=a) for a in ((0,-5,0),(0,0,0),(0,3,0),(3,6,4),(6,2,8))]
    skel = Bones(jnts)
    print "Twist Joint".center(20, "-")
    print repr(jnts[1])
    print "Skip Twist".center(20, "-")
    print repr(skel.get_real_joint(jnts[1]))
    print "Skeleton".center(20, "-")
    print skel
