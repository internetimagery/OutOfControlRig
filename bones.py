# Skeleton stuff

import pymel.core as pmc
import collections
import traceback

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
            if joint in limb: return tuple(a for a, b in limb.iteritems() if b)

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
                vec1 = jnt2.getTranslation("world") - jnt1.getTranslation("world")
                vec2 = jnt3.getTranslation("world") - jnt2.getTranslation("world")
                dot = vec1 * vec2
                if vec1.isParallel(vec2): # Flag twist joint
                    limb[jnt2] = False
                else:
                    limb[jnt2] = True
                    jnt2.displayLocalAxis.set(1) # Mark joints that bend
            limb[jnt3] = True # End joint can't be twist
        return limb

    def temp_ik(s, joint):
        """ Build a temporary IK chain onto joint chain """
        for limb in s.limbs:
            if joint in limb:
                working_limb = limb
                break
        else: return # No result? Stop early

        secondary_limb = collections.OrderedDict()
        found = False
        root = end = None # Two ends of our IK chain
        pmc.select(clear=True)
        for i, (jnt, twist) in enumerate(working_limb.iteritems()): # Build short limb
            if jnt == joint: found = True
            if not i and jnt == joint: return # No IK on root joint
            if twist:
                pos = jnt.getTranslation("world")
                new_jnt = pmc.joint(p=pos)
                secondary_limb[new_jnt] = jnt
                if root:
                    end = new_jnt
                else:
                    root = new_jnt
                if found: break # Stop on selected joint

        constraints = [pmc.orientConstraint(a, b, mo=True) for a, b in secondary_limb.iteritems()]
        handle, effector = pmc.ikHandle(sj=root, ee=end)
        pmc.orientConstraint(handle, new_jnt, mo=True)

        def removal(): # Remove IK chain!
            state = pmc.autoKeyframe(q=True, st=True)
            pmc.autoKeyframe(st=False)
            try:
                for i, (jnt1, jnt2) in enumerate(secondary_limb.iteritems()):
                    pmc.setKeyframe(jnt2.rotate)
                    if not i: root = jnt1
                pmc.delete(root)
            except:
                print traceback.format_exc(); raise
            finally:
                pmc.autoKeyframe(st=state)

        pmc.scriptJob(e=["SelectionChanged", removal], ro=True) # Remove IK upon selection change

        return handle

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    joints = [pmc.joint(p=a) for a in ((0,-5,0),(0,0,0),(0,3,0),(3,6,4))]
    skel = Skeleton(joints)
    assert joints[2] in skel
    assert skel.get(joints[1]) == joints[2] # Skip twist joint
    print skel.get_limb(joints[1])
    def IK_test():
        try:
            sel = pmc.ls(sl=True, type="joint")
            if sel:
                print "IK", sel[0]
                skel.temp_ik(sel[0])
        except:
            print traceback.format_exc(); raise
    pmc.scriptJob(e=["SelectionChanged", IK_test], kws=True)
