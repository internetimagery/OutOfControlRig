# Skeleton stuff

import pymel.core as pmc
import contextlib
import collections
import traceback

@contextlib.contextmanager
def save_position(joints):
    """ Save the position of joints after changes have been made """
    pos = dict((a, (a.translate.get(), a.rotate.get())) for a in joints)
    try:
        yield
    finally:
        for jnt, (p, r) in pos.iteritems():
            jnt.translate.set(p)
            jnt.rotate.set(r)

@contextlib.contextmanager
def script_job_debug():
    """ Print out errors even while in scriptjobs """
    try:
        yield
    except:
        print traceback.format_exc(); raise

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
        try:
            for limb in s.limbs:
                if joint in limb:
                    working_limb = []
                    found = False
                    for jnt, twist in limb.iteritems(): # Strip out twist joints
                        if twist: working_limb.append(jnt)
                        if jnt == joint: raise StopIteration
        except StopIteration:
            pass
        else:
            print "Requested joint not in cache..."
            return # No result? Stop early

        if len(working_limb) < 2: return # We are on the root joint

        secondary_limb = collections.OrderedDict()
        pmc.select(clear=True)
        for i, jnt in enumerate(working_limb): # Build short limb
            pos = jnt.getTranslation("world")
            new = pmc.joint(p=pos)
            secondary_limb[new] = jnt
            pmc.orientConstraint(new, jnt, mo=True)
            if i:
                end = new
            else:
                root = new

        handle, effector = pmc.ikHandle(sj=root, ee=end)
        handle.visibility.set(0) # Hide handle
        controller = pmc.group(em=True) # Set up controller
        pmc.xform(controller,
            roo=pmc.xform(jnt, q=True, roo=True),
            t=pmc.xform(jnt, q=True, ws=True, t=True),
            ro=pmc.xform(jnt, q=True, ws=True, ro=True),
            ws=True
        )
        pmc.pointConstraint(controller, handle, mo=True)
        pmc.orientConstraint(controller, end, mo=True)

# om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, func) # make changes before save
# om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, func) # put everything back

        def set_pos():
            with script_job_debug():
                with save_position(b for a, b in secondary_limb.iteritems()):
                    pass

        def removal(): # Remove IK chain!
            with script_job_debug():
                with save_position(b for a, b in secondary_limb.iteritems()):
                    pmc.scriptJob(kill=set_job)
                    for jnt in secondary_limb:
                        if jnt.exists():
                            pmc.delete(jnt)
                    if controller.exists(): pmc.delete(controller)

        pmc.select(controller, r=True)
        set_job = pmc.scriptJob(ac=[controller.translate, set_pos], kws=True)
        pmc.scriptJob(e=["SelectionChanged", removal], ro=True) # Remove IK upon selection change

        return controller

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    joints = [pmc.joint(p=a) for a in ((0,-5,0),(0,0,0),(0,3,0),(3,6,4),(6,2,8))]
    skel = Skeleton(joints)
    assert joints[2] in skel
    assert skel.get(joints[1]) == joints[2] # Skip twist joint
    print skel.get_limb(joints[1])
    def IK_test():
        with script_job_debug():
            sel = pmc.ls(sl=True, type="joint")
            if len(sel) == 1:
                print "IK", sel[0]
                skel.temp_ik(sel[0])
    joints[2].rotateX.set(20)
    pmc.scriptJob(e=["SelectionChanged", IK_test], kws=True)
