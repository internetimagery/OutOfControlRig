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

# import track
import OutOfControlRig.track as track
import pymel.core as pmc
import maya.api.OpenMaya as om # Use new API
import maya.api.OpenMayaUI as omui

class Picker(object):
    """ Picker tool. Return point on mesh clicked """
    def __init__(s):
        s.name = "OutOfControlPicker"
        s.whitelist = [] # List of meshes to check against
        s.callback_start = None # Callback
        s.callback_click = None # Callback
        s.callback_drag = None # Callback
        s.callback_stop = None # Callback
        s._last_tool = pmc.currentCtx() # Last tool used

        s.kill() # Clear out last tool if there
        pmc.context.draggerContext(
            s.name,
            name=s.name,
            releaseCommand=s.call_click,
            dragCommand=s.call_drag,
            cursor="hand",
            image1="hands.png"
        )

        s.tracker = tracker = track.Tool(p=s.name)
        tracker.callback = s._tool_changed # Watch for tool changes

    def set(s):
        """ Activate Tool """
        last_tool, name = pmc.currentCtx(), s.name
        if last_tool != name:
            s._last_tool = last_tool
            pmc.setToolTo(name) # Set our tool to the active tool

    def unset(s):
        """ Set us back to the last tool """
        pmc.setToolTo(s._last_tool)

    def _tool_changed(s, tool):
        """ Watch for tool changes """
        call1, call2 = s.callback_start, s.callback_stop
        if tool == s.name and call1:
            call1() # Changed to our tool
        elif call2:
            s._last_tool = pmc.currentCtx() # Track tool changes
            call2() # Changed away from our tool

    @property
    def active(s):
        """ Check if tool is currently active """
        return pmc.currentCtx() == s.name

    def call_click(s):
        """ Call back click events """
        call = s.callback_click
        if call: call(*s._pick_point())

    def call_drag(s):
        """ Call back drag events """
        call = s.callback_drag
        if call: call(*s._pick_point())

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
                intersection = om.MFnMesh(sel.getDagPath(0)).closestIntersection(*ray_args)
                if intersection and intersection[3] != -1: # We have a hit!
                    return w.getShape(), intersection[2] # Hit mesh, and face ID
        except RuntimeError as e:
            print "Err", e
        return None, None

    def kill(s):
        """ Stop the tracker... in its tracks! get it! """
        if pmc.context.draggerContext(s.name, ex=True):
            pmc.deleteUI(s.name)

if __name__ == '__main__':
    # Testing
    def start():
        print "Tool started."
    def stop():
        print "Tool stopped."
    def clicked(*args):
        print "Clicked!", args
    def dragged(*args):
        print "Dragging!", args
    pmc.system.newFile(force=True)
    xform1 = pmc.polyCylinder()[0] # Create a cylinder
    xform2 = pmc.sphere(p=(2,0,0))[0]
    p = Picker()
    p.whitelist = [xform1, xform2] # Add object to our whitelist
    p.callback_start = start
    p.callback_click = clicked # Add our callback
    p.callback_drag = dragged # Add our callback
    p.callback_stop = stop
    p.set()
