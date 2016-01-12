# Out of Control Rig!
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

# TODO: make this work if it were in a shelf icon. gui can do additional setup for this to operate

import pymel.core as pmc
import maya.api.OpenMaya as om
import OutOfControlRig.tool as tool
import OutOfControlRig.cache as cache
import OutOfControlRig.colour as colour
import OutOfControlRig.temp_IK as temp_IK
import OutOfControlRig.skeleton as skeleton
import OutOfControlRig.collection as collection

RIG_NAME = "OutOfControlRig"
GREEN = (0.3, 0.8, 0.1)
YELLOW = (9.0, 0.7, 0.3)

class Rig(object):
    """ Rig!! """
    def __init__(s):
        s.running = False
        s.refresh_whitelist()
        s.tool = tool.Picker( # Initialize our tool
            meshes=lambda: s.whitelist,
            start=s.rig_build,
            stop=s.rig_teardown,
            drag=s.drag_highlight,
            click=s.click_highlight,
        )
        # pmc.scriptJob(e=("PostSceneRead", s.refresh_whitelist)) # Keep whitelist up to date
        # pmc.scriptJob(e=("NewSceneOpened", s.refresh_whitelist))

    def set(s):
        """ Set tool """
        s.tool.set()

    def refresh_whitelist(s):
        """ Collect data from the scene """
        selection = pmc.ls(RIG_NAME, r=True, type="objectSet")
        s.whitelist = filtered_selection = set(c for a in selection for b in a for c in b.getShapes())
        s.cache_inf, s.cache_pref = cache.preferred_joint_and_influence(filtered_selection)
        s.cache_skele = skeleton.Bones(s.cache_inf)

    def rig_build(s):
        """ build up rig """
        running = True
        for w in s.whitelist: colour.paint(w)

    def rig_teardown(s):
        """ remove up rig """
        running = False
        for w in s.whitelist: colour.erase(w)

    def drag_highlight(s, obj, face_id):
        """ highlight meshes """
        if obj:
            string_name = om.MFnDagNode(obj).fullPathName()
            node = pmc.PyNode(string_name) # Convert to pymel again, boo!
            try:
                joint = s.cache_pref[node][face_id]
                influence = s.cache_inf[joint]
                colour.paint(influence, YELLOW)
                pmc.refresh()
            except KeyError as e:
                print "Missing node", e

    def click_highlight(s, obj, face_id):
        """ highlight meshes """
        if obj:
            string_name = om.MFnDagNode(obj).fullPathName()
            node = pmc.PyNode(string_name) # Convert to pymel again
            try:
                joint = s.cache_pref[node][face_id]
                # influence = s.cache_inf[joint]
                # colour.paint(influence, GREEN)
                s.tool.unset()
                limb = s.cache_skele.get_partial_limb(joint)
                temp_IK.control(limb)
            except KeyError:
                print "Missing node", node

if __name__ == '__main__':
    # Testing
    import random
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder(sy=5, h=6) # Create a cylinder and joints
    jnts = [pmc.joint(p=(0,b,random.random() * 0.5)) for b in (a for a in range(-3, 4))]
    sk = pmc.skinCluster(jnts[0], xform, mi=1) # Bind them to the cylinder
    pmc.select(xform, r=True)
    pmc.sets(n=RIG_NAME)
    Rig().set()
