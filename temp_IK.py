# Temporary IK chain to provide translation control to joints.

import functools
import traceback
import collections
import pymel.core as pmc
import maya.api.OpenMaya as om

TEARDOWN_QUEUE = set()
def before_save(*_):
    funcs = TEARDOWN_QUEUE.copy()
    TEARDOWN_QUEUE.clear()
    for func in funcs: func()
om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, before_save) # make changes before save

SETUP_QUEUE = set()
def after_save(*_):
    funcs = SETUP_QUEUE.copy()
    SETUP_QUEUE.clear()
    for func in funcs: func()
om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, after_save) # put everything back

def scriptJob(func):
    """ Display Errors when running scriptjob """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print traceback.format_exc()
            raise
    return inner

@scriptJob
def control(joint_chain):
    """ Build a temporary IK chain and select the handle """
    print "CREATING JOINT"
    chain_num = len(joint_chain)
    if not chain_num: return # Nothing to select
    if chain_num == 1: return pmc.select(joint_chain[0], r=True) # No need for IK on a single joint chain

    pmc.select(clear=True)
    temp_chain = tuple(pmc.joint(p=a.getTranslation("world")) for a in joint_chain)
    constraints = tuple(pmc.orientConstraint(*a, mo=True) for a in zip(temp_chain, joint_chain))

    handle, effector = pmc.ikHandle(sj=temp_chain[0], ee=temp_chain[-1])
    handle.visibility.set(0) # hide chain

    controller = pmc.group(em=True)
    controller.setMatrix(temp_chain[-1].getMatrix(ws=True))
    pmc.pointConstraint(controller, handle, mo=True)
    pmc.orientConstraint(controller, temp_chain[-1], mo=True)

    @scriptJob
    def controller_moved(): # Track controller movements
        print "Controller Moved!"

    @scriptJob
    def select_control(): # Delayed for scene save conveniences
        print "SELECTING"
        if controller.exists():
            pmc.select(controller, r=True)
            pmc.scriptJob(e=("SelectionChanged", remove), ro=True)

    @scriptJob
    def remove(): # Remove the chain
        print "REMOVING JOINT"
        TEARDOWN_QUEUE.discard(teardown)
        matrices = tuple(a.getMatrix(ws=True) for a in joint_chain)
        try:
            pmc.delete(controller)
            pmc.delete(temp_chain[0])
        except pmc.MayaNodeError:
            pass
        for jnt, m in zip(joint_chain, matrices): jnt.setMatrix(m, ws=True)

    @scriptJob
    def teardown(): # Tear down the chain on save
        print "TEARDOWN!"
        remove()
        SETUP_QUEUE.add(functools.partial(control, joint_chain))

    pmc.scriptJob(ie=select_control, ro=True) # Select our controller
    pmc.scriptJob(ac=(controller.translate, controller_moved), kws=True)
    TEARDOWN_QUEUE.add(teardown)


if __name__ == '__main__':
    # Testing. Build a new scene with a simple random joint chain
    import random, itertools
    pmc.system.newFile(force=True)
    def random_pos(): return (random.random() * 10 - 5 for a in range(3))
    joints = [pmc.joint(p=random_pos()) for a in range(3)]
    @scriptJob
    def select_joint():
        sel = pmc.ls(sl=True, type="joint")
        if len(sel) == 1:
            control(joints[:joints.index(sel[0]) + 1])
    print "Select a joint and move it around."
    pmc.select(clear=True)
    pmc.scriptJob(e=("SelectionChanged", select_joint), kws=True)


#     def set_pos():
#         with script_job_debug():
#             with save_position(b for a, b in secondary_limb.iteritems()):
#                 pass
#
#     def teardown(): # Avoid saving our setup in scene file
#         removal()
#         SETUP_QUEUE.add(setup)
#
#     def setup(): # Put everything back
#         s.temp_ik(joint) # Rebuild
#
#     def removal(): # Remove IK chain!
#         TEARDOWN_QUEUE.discard(teardown)
#         SETUP_QUEUE.discard(setup)
#         with script_job_debug():
#             if controller.exists():
#                 with save_position(secondary_limb.values()):
#                     for jnt in secondary_limb:
#                         if jnt.exists():
#                             pmc.delete(jnt)
#                             break # Only need to delete the root joint
#                     pmc.delete(controller)
#
#     def select_controller(): # Delay execution to re-select after scene save
#         pmc.select(controller, r=True)
#         pmc.scriptJob(e=["SelectionChanged", removal], ro=True) # Remove IK upon selection change
#         pmc.scriptJob(ac=[controller.translate, set_pos], kws=True)
#     pmc.scriptJob(ie=select_controller, ro=True)
#
#     # Teardown and setup during attempted scene saves
#     TEARDOWN_QUEUE.add(teardown)
#
#     return controller
