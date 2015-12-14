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

def missing(*_):
    raise NotImplementedError

class Picker(object):
    """ Picker tool. Return point on mesh clicked """
    def __init__(s, whitelist=missing, start=missing, stop=missing, click=missing, drag=missing):
        s.name = "OutOfControlPicker"
        s.active = False # tool state
        s.whitelist = whitelist # List of meshes to check against
        s.callback_start = start # Callback
        s.callback_stop = stop # Callback
        s.callback_click = click # Callback
        s.callback_drag = drag # Callback
        s.last_tool = pmc.currentCtx() # Last tool used

        s.kill() # Clear out last tool if there
        pmc.context.draggerContext(
            s.name,
            name=s.name,
            releaseCommand=s.call_click,
            dragCommand=s.call_drag,
            cursor="hand",
            image1="hands.png",
            undoMode="sequence",
        )

        # Track tool changes, allowing us to track previous tool
        pmc.scriptJob(e=("PostToolChanged", s.track_change),p=s.name)

    def set(s):
        """ Activate Tool """
        last_tool, name = pmc.currentCtx(), s.name
        if last_tool != name:
            s.last_tool = last_tool
            pmc.setToolTo(name) # Set our tool to the active tool

    def unset(s):
        """ Set us back to the last tool """
        pmc.setToolTo(s.last_tool)

    def track_change(s):
        """ Watch for tool changes """
        tool = pmc.currentCtx()
        call1, call2 = s.callback_start, s.callback_stop
        if tool == s.name:
            if not s.active: # Not yet running
                s.active = True
                if call1: call1()
        else:
            if s.active: # Turning off
                s.active = False
                if call2: call2()
            s.last_tool = tool

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
            for w in s.whitelist():
                sel = om.MSelectionList() # New selection list
                sel.add(str(w)) # Add object
                intersection = om.MFnMesh(sel.getDagPath(0)).closestIntersection(*ray_args)
                if intersection and intersection[3] != -1: # We have a hit!
                    return w.getShape(), intersection[2] # Hit mesh, and face ID
        except RuntimeError:
            pass
        return None, None

    def kill(s):
        """ Stop the tracker... in its tracks! get it! """
        if pmc.context.draggerContext(s.name, ex=True):
            pmc.deleteUI(s.name)

if __name__ == '__main__':
    # Testing
    import random
    def start():
        print "Tool started".center(20, "-")
    def stop():
        print "Tool stopped".center(20, "-")
    def clicked(*args):
        print "Clicked!".center(20, "-")
        print args
    def dragged(*args):
        print "Dragging!".center(20, "-")
        print args
    def rand_pos(): return [random.random() * 10 - 5 for a in range(3)]
    pmc.system.newFile(force=True)
    objs = [pmc.polySphere()[0] for a in range(3)]
    for o in objs: pmc.xform(o, t=rand_pos())
    p = Picker(
        (lambda: objs),
        start,
        stop,
        clicked,
        dragged
    )
    p.set()
    print "Click something".center(20, "-")
