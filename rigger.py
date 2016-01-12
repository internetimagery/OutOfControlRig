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

    def rig_build(s):
        """ build up rig """
        print "build rig".center(20, "-")
        running = True

    def rig_teardown(s):
        """ remove up rig """
        print "remove rig".center(20, "-")
        running = False

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
                influence = s.cache_inf[joint]
                colour.paint(influence, GREEN)
                pmc.select(joint, r=True)
                s.tool.unset()
            except KeyError:
                print "Missing node", node

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder(sy=5) # Create a cylinder and joints
    jnt1, jnt2, jnt3 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,0,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform, mi=1) # Bind them to the cylinder
    pmc.select(xform, r=True)
    pmc.sets(n=RIG_NAME)
    Rig().set()
