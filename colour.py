# Set Vertex colours on object
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

BASE_COLOUR = (0.5,0.5,0.5) # Base colour

class Canvas(object):
    """ Paint objects """
    base_colour = (0.5,0.5,0.5)
    def __init__(s):
        s.last_colour = None

    def paint(s, selection, colour=None):
        """ Paint some colour on objects """
        colour = colour or s.base_colour
        pmc.polyColorPerVertex(s.last_colour, rgb=s.base_colour, cdo=True)
        pmc.polyColorPerVertex(selection, rgb=colour, cdo=True)
        s.last_colour = selection

    def erase(s, geos):
        """ Wipe out colour on objects """
        for m in meshes: pmc.setAttr("%s.displayColors" % m, 0)


def paint(selection, colour=None):
    """ Set the colour of selection to be whatever """
    if colour:
        pmc.polyColorPerVertex(selection, rgb=colour, cdo=True)
    else:
        pmc.polyColorPerVertex(selection, rgb=BASE_COLOUR, cdo=True)

def erase(meshes):
    """ Remove colours on meshes """
    for m in meshes: pmc.setAttr("%s.displayColors" % m, 0)

if __name__ == '__main__':
    # Testing
    import time
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    paint("%s.vtx[0:]" % xform, (0.2,0.6,0.7))
    for i in range(10):
        pmc.refresh()
        time.sleep(0.1)
    erase([xform])
