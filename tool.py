# Picker tool
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
import maya.api.OpenMaya as om # Use new API
import maya.api.OpenMayaUI as omui


class Picker(object):
    """ Picker tool. Return point on mesh clicked """
    def __init__(s):
        s.name = "OutOfControlPicker"
        s.whitelist = set() # List of meshes to check against
        s.callback_click = set()
        s.callback_drag = set() # Callbacks
        s.last_tool = None # Last tool used
        s._create()

    def set(s):
        """ Activate Tool """
        s.last_tool = pmc.currentCtx()
        # FOR DEBUG, REMOVE AND RECREATE TOOL EACH TIME IT IS CREATED
        s._create()
        # END DEBUG SECTION!! TODO: PUT THIS INTO ITS OWN CREATION FUNCTION AND CALL ONCE
        pmc.setToolTo(s.name) # Set our tool to the active tool

    def unset(s):
        """ Set us back to the last tool """
        pmc.setToolTo(s.last_tool)

    def _create(s):
        """ Create our tool """
        if pmc.context.draggerContext(s.name, ex=True): pmc.deleteUI(s.name)
        pmc.context.draggerContext(
            s.name,
            name=s.name,
            releaseCommand=s.call_click,
            dragCommand=s.call_drag,
            cursor="hand",
            image1="hands.png"
        )
    @property
    def active(s):
        """ Check if tool is currently active """
        return pmc.currentCtx() == s.name

    def call_click(s):
        """ Call back click events """
        mesh, ID = s._pick_point() # Get point in space
        for call in s.callback_click:
            call(mesh, ID)

    def call_drag(s):
        """ Call back drag events """
        mesh, ID = s._pick_point() # Get point in space
        for call in s.callback_drag:
            call(mesh, ID)

    def _pick_point(s):
        """ Pick a point on mesh from where user clicked """
        try:
            # Get our Screen position
            viewX, viewY, viewZ = pmc.context.draggerContext(s.name, q=True, dp=True)
            # Using Maya API
            position = om.MPoint() # Placeholder position
            direction = om.MVector() # Placeholder
            # Convert 2D position on screen into a 3D world space position
            omui.M3dView().active3dView().viewToWorld(int(viewX), int(viewY), position, direction)
            # Run through our whitelist, casting a ray on each and checking for hits
            ray_args = (om.MFloatPoint(position), om.MFloatVector(direction), om.MSpace.kWorld, 99999, False)
            for w in s.whitelist:
                sel = om.MSelectionList() # New selection list
                sel.add(str(w)) # Add object
                obj = om.MFnMesh(sel.getDagPath(0)) # Get our DAG Path
                intersection = obj.closestIntersection(*ray_args)
                if intersection and intersection[3] != -1: # We have a hit!
                    return w, intersection[2] # Hit mesh, and face ID
        except RuntimeError as e:
            print "Err", e
        return None, None

Picker = Picker() # Initialize

if __name__ == '__main__':
    # Testing
    def clicked(*args):
        print "Clicked!", args
    def dragged(*args):
        print "Dragging!", args
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    Picker.whitelist.add(xform) # Add object to our whitelist
    Picker.callback_click.add(clicked) # Add our callback
    Picker.callback_drag.add(dragged) # Add our callback
    Picker.set()
