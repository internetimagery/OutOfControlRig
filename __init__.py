# Controllerless Rig Setup
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
import pymel.core.windows as pmw
import functools
import sys

def unique_class(cls):
    """ Keep only one instance of class active """
    instances = {}

    @functools.wraps(cls)
    def unique_cls(*args, **kwargs):
        if (cls in instances and sys.getrefcount(instances[cls]) < 3) or cls not in instances:
            instances[cls] = instance = cls(*args, **kwargs)
        return instance
    return unique_cls

@unique_class
class Main(object):
    """ Main Window. Rig Tool runs while window is open """
    def __init__(s):
        sel = pmc.ls(sl=True, type="transform")
        if not sel: raise RuntimeError, "You must select your rigs mesh."
        title = "Out of Control Rig!"
        win = pmw.window(t=title)
        pmw.columnLayout(adj=True)
        pmw.button(l='Click Me', h=25)
        allowed_areas = ['right', 'left']
        s._dock = pmw.dockControl(
            l=title,
            a='left',
            aa=allowed_areas,
            fl=True,
            content=win,
            fcc=s._dock_moved,
            vcc=s._dock_closed)
        s._dock_query = functools.partial(pmw.dockControl, s._dock, q=True)
        location = s._dock_get_loc()
        if location in allowed_areas:
            pmw.dockControl(s._dock, e=True, a=location)
        else:
            pmw.dockControl(s._dock, e=True, fl=True)

    def _dock_moved(s):  # Update dock location information
        if s._dock_query(fl=True):
            s._dock_set_loc("float")
            print "Floating Dock."
        else:
            area = s._dock_query(a=True)
            s._dock_set_loc(area)
            print "Docking %s." % area

    def _dock_closed(s, *loop):
        visible = s._dock_query(vis=True)
        if not visible and loop:
            pmc.scriptJob(ie=s._dock_closed, p=s._dock, ro=True)
        elif not visible:
            pmw.deleteUI(s._dock, control=True)
            print "Window closed."

    def _dock_get_loc(s):
        """ Get location from preferences """
        return "float"  # You can replace this with code that loads persistant data

    def _dock_set_loc(s, location):
        """ Set location in preferences """
        s.location = location  # You can replace this with code that saves persistant data

if __name__ == '__main__':
    Main()
