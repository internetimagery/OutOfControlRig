# Skeleton stuff

import pymel.core as pmc
import collections

class Skeleton(collections.Set):
    """ Skeleton. Contains limbs """
    def __init__(s, joints):
        tmp_limbs = []
        for joint in joints:
            try:
                for limb in tmp_limbs:
                    if joint in limb: raise StopIteration
                tmp_limbs.append(s._build_limb(joint))
            except StopIteration:
                pass
        s.limbs = tuple(tmp_limbs)

    def __len__(s):
        """ Number of joints in skeleton """
        return sum(len(a) for a in s.limbs)

    def __iter__(s):
        """ Walk through joints in skeleton """
        for limb in s.limbs:
            for joint, twist in limb.iteritems():
                yield joint, twist

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

    def get(s, joint):
        """ Given a joint name, get corresponding non-twist joint """
        for limb in s.limbs:
            if joint in limb:
                start = False # Looped up to the joint?
                for jnt, twist in limb.iteritems():
                    if jnt == joint: start = True # Start the real loop!
                    if start and twist: return jnt # Return next non-twist joint

    def get_limb(s, joint):
        """ Given a joint, get the corresponding limb """
        for limb in s.limbs:
            if joint in limb: return limb

    def _build_limb(s, joint):
        """ Given a joint, form a limb """
        chain = []
        def walk(jnt):
            chain.append(jnt)
            children = jnt.getChildren()
            if len(children) == 1:
                walk(children[0])
        walk(joint) # Walk down the chain

        parents = joint.getAllParents()
        for parent in parents: # Walk towards root
            children = parent.getChildren()
            if len(children) == 1:
                chain.insert(0, parent)
        # Now we have a complete limb!!

        # Flag parallel joints as twist joints
        limb = collections.OrderedDict()
        chain_num = len(chain) # Number of elements
        if len(chain) < 3: # Too small to contain twist joints
            for i in range(chain_num):
                limb[chain[i]] = True # Mark as standalone joint
        else:
            limb[chain[0]] = True # Root can't be twist joint
            chain[0].displayLocalAxis.set(1) # Mark joints that bend
            for i in range(chain_num - 2): # Joint chain is long enough to be complex
                jnt1, jnt2, jnt3 = chain[i], chain[i+1], chain[i+2]
                vec1 = jnt2.getTranslation() - jnt1.getTranslation()
                vec2 = jnt3.getTranslation() - jnt2.getTranslation()
                dot = vec1 * vec2
                if vec1.isParallel(vec2): # Flag twist joint
                    limb[jnt2] = False
                else:
                    limb[jnt2] = True
                    jnt2.displayLocalAxis.set(1) # Mark joints that bend
            limb[jnt3] = True # End joint can't be twist
        return limb

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    joints = [pmc.joint(p=a) for a in ((0,-5,0),(0,0,0),(0,3,0),(3,6,4))]
    skel = Skeleton(joints)
    assert joints[2] in skel
    assert skel.get(joints[1]) == joints[2] # Skip twist joint
    print skel
