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

import pymel.core as pmc
import OutOfControlRig.has as has
import OutOfControlRig.tool as tool
import OutOfControlRig.cache as cache
import OutOfControlRig.track as track
import OutOfControlRig.colour as colour

# Colours
GREEN = (0.3, 0.8, 0.1)
YELLOW = (9.0, 0.7, 0.3)

class Control(object):
    """ Control the rig ... controllerlessly? """
    def __init__(s, geos):
        # Cache our mesh information
        s.cache(geos)

        # Set up our picker tool
        s.picker = picker = tool.Picker() # Picker tool
        picker.whitelist = geos
        picker.callback_start = s.activate_rig
        picker.callback_click = s.picked
        picker.callback_drag = s.dragging
        picker.callback_stop = s.deactivate_rig
        picker.set()

        s.canvas = colour.Canvas()

        # Set up our selection tracker
        track.Selection(kws=True).callback = s.selection_changed

        s.drag_joint = None # Last joint visited

        # States
        s.making_selection = False # If we are changing the tool ourselves
        s.controlling_rig = False # Currently controlling the rig

    def cache(s, geos):
        """ Cache some meshes for use """
        s.geos = geos = dict((a, has.skin(a)) for a in geos) # Get skins
        s.cache_influence, s.cache_pref = cache.preferred_joint_and_influence()
        s.cache_all = ",".join("%s.vtx[0:]" % a for a in geos) # Everything!

    def activate_rig(s):
        """ turn on our rig """
        if s.making_selection: return
        colour.paint(s.cache_all) # Paint everything grey

    def deactivate_rig(s):
        """ turn off the rig """
        if s.making_selection: return
        s.canvas.paint(s.cache_all) # Paint it all grey and...
        s.canvas.erase(s.geos) # Clear our colour information

    def picked(s, mesh, ID):
        """ clicked on a mesh """
        try:
            s.drag_joint = None # Clear last joint
            colour.paint(s.cache_all) # Clear canvas
            if mesh: # Did we select anything?
                joint = s.cache_weights[mesh][ID] # Selected joint
                canvas = s.cache_influence[joint]
                s.canvas.paint(canvas, YELLOW)
                s.make_selection(joint) # Select the joint
        except KeyError:
            print "Joint missing from cache."

    def dragging(s, mesh, ID):
        """ dragging mesh """
        try:
            if mesh: # Are we still dragging on the mesh?
                joint = s.cache_weights[mesh][ID]
                if joint != s.drag_joint:
                    s.drag_joint = joint
                    canvas = s.cache_influence[joint]
                    s.canvas.paint(s.cache_all) # Clear canvas
                    s.canvas.paint(canvas, GREEN)
                    pmc.refresh() # Update display
        except KeyError:
            print "Joint missing from cache."

    def selection_changed(s, sel):
        """ Selection has been changed """
        if s.controlling_rig: # We were controlling the rig
            s.controlling_rig = False
            s.deactivate_rig()

        if s.making_selection: # We are in the process of making a selection
            s.making_selection = False # Reset
            s.controlling_rig = True # We are now controlling the rig

    def make_selection(s, joint):
        """ select control object """
        pmc.select(joint, r=True) # TODO: make this more sophisticated
        s.making_selection = True # We are ready for this change
        s.picker.unset() # Return to previous tool

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder(sy=5) # Create a cylinder and joints
    jnt1, jnt2, jnt3 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,0,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform, mi=1) # Bind them to the cylinder
    Control([xform])
    pmc.select(clear=True)
