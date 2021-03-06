# Temporary IK chain to provide intuitive translation control to joint chains.
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

# TODO: Make it work nice with existing constraint setups. Orient / Aim / Parent
# TODO: Work with locked rotation attributes
# TODO: Correctly twist the Twist joints.

import functools
import traceback
import pymel.core as pmc
from maya.api.OpenMaya import MSceneMessage as scene
import maya.api.OpenMaya as om

KEY = functools.partial(pmc.keyframe, q=True, tc=True, vc=True)
RESET = {
    "aimConstraint": lambda x: cmds.aimConstraint(x, e=True, mo=True),
    "pointConstraint": lambda x: cmds.pointConstraint(x, e=True, mo=True),
    "orientConstraint": lambda x: cmds.orientConstraint(x, e=True, mo=True),
    "parentConstraint": lambda x: cmds.parentConstraint(cmds.parentConstraint(x, q=True, tl=True), x, e=True, mo=True)
}

TEARDOWN_QUEUE = set()
def before_save(*_):
    """ Teardown IK before save """
    funcs = TEARDOWN_QUEUE.copy()
    TEARDOWN_QUEUE.clear()
    for func in funcs: func()
scene.addCallback(scene.kBeforeSave, before_save) # make changes before save

SETUP_QUEUE = set()
def after_save(*_):
    """ Rebuild IK after save """
    funcs = SETUP_QUEUE.copy()
    SETUP_QUEUE.clear()
    for func in funcs: func()
scene.addCallback(scene.kAfterSave, after_save) # put everything back

def scriptJob(func):
    """ Display Errors when running scriptjob """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print traceback.format_exc()
            raise
    return inner

def control(joint_chain):
    """ Build a temporary IK chain and select the handle """
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
        new_keys = frozenset(KEY(controller.translate))
        old_keys = controller_moved.keys
        if new_keys != old_keys: # If our controller is keyed. Transfer keys onto joints.
            controller_moved.keys = new_keys
            changed = frozenset(a[0] for a in new_keys ^ old_keys) # Get time changed
            curr_time = last_time = pmc.currentTime(q=True)
            try:
                for time in changed:
                    if time != last_time:
                        pmc.currentTime(q=True)
                        last_time = time
                    for jnt, con in zip(joint_chain, constraints):
                        pmc.setKeyframe(jnt.rotate)
                        for blend in set(con.outputs(type="pairBlend")):
                            for attr in blend.weight.inputs(p=True):
                                attr.set(1) # Keep blend from messing with us
            finally:
                if curr_time != last_time:
                    pmc.currentTime(curr_time)

    @scriptJob
    def select_control(): # Delayed for scene save conveniences
        pmc.select(controller, r=True)
        select_control.sel = pmc.scriptJob(e=("SelectionChanged", remove), ro=True)

    @scriptJob
    def remove(from_scriptJob=True): # Remove the chain
        if not from_scriptJob: pmc.scriptJob(kill=select_control.sel) # Cannot kill scriptJob while in scriptJob
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
        remove(False)
        SETUP_QUEUE.add(functools.partial(control, joint_chain))

    if pmc.autoKeyframe(q=True, st=True): controller.translate.setKey() # Prep autokey
    controller_moved.keys = frozenset(KEY(controller.translate))
    pmc.scriptJob(ie=select_control, ro=True) # Select our controller
    pmc.scriptJob(ac=(controller.translate, controller_moved), kws=True)
    TEARDOWN_QUEUE.add(teardown)
    return controller


if __name__ == '__main__':
    # Testing. Build a new scene with a simple random joint chain
    import random, itertools
    num_joints = 4
    pmc.system.newFile(force=True)
    def random_pos(): return (random.random() * 10 - 5 for a in range(3))
    joints = [pmc.joint(p=random_pos()) for a in range(num_joints)]
    @scriptJob
    def select_joint():
        sel = pmc.ls(sl=True, type="joint")
        if len(sel) == 1:
            pmc.scriptJob(ro=True, ie=lambda:control(joints[:joints.index(sel[0]) + 1]))

    print "Select a joint and move it around..."
    pmc.select(clear=True)
    pmc.scriptJob(e=("SelectionChanged", select_joint), kws=True)
