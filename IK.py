# IK chain functionality

import pymel.core as pmc


def get_ik(jnt):
    """ Get any IK handles attached to joint, if one exists """
    ik_handles = [set(e.connections(s=False, type="ikHandle")).pop() for e in set(jnt.connections(s=False, type="ikEffector"))]
    return ik_handles

def new_ik(start, middle, end=None):
    """ Create an IK joint """
    handle, effector = pmc.ikHandle(sj=start, ee=middle)
    if end: # Things get complicated!
        end_pos = end.getTranslation("world")
        pmc.xform(effector, rp=end_pos, sp=end_pos, ws=True)
        pmc.xform(handle, t=end_pos, ws=True)

        pmc.xform(handle, roo=pmc.xform(end, q=True, roo=True)) # Match rotation order
        pmc.xform(handle, ro=pmc.xform(end, q=True, ro=True)) # Match rotation angle

        constraint = pmc.orientConstraint(handle, end)

    return handle



if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    joints = [pmc.joint(p=a) for a in ((10,-5,0),(0,0,0),(0,3,0),(0,8,0))]
    print new_ik(joints[0], joints[2], joints[-1])
