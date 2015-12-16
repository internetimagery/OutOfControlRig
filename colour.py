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

def paint(selection, colour=None):
    """ Colour selection """
    colour = colour or BASE_COLOUR
    if paint.last:
        try:
            pmc.polyColorPerVertex(paint.last, rgb=BASE_COLOUR, cdo=True)
        except RuntimeError as e:
            print e
    pmc.polyColorPerVertex(selection, rgb=colour, cdo=True)
    paint.last = selection
paint.last = None

def erase(mesh):
    """ Clear / Prepare colour on mesh """
    pmc.polyColorPerVertex(mesh.vtx, rgb=BASE_COLOUR)
    mesh.displayColors.set(0)

if __name__ == '__main__':
    # Testing
    import time, threading, random
    from maya.utils import executeInMainThreadWithResult as ex
    pmc.system.newFile(force=True)
    xform, shape = pmc.polySphere() # Create a cylinder and joints
    vert_num = xform.numVertices() - 1
    erase(xform)
    def flip():
        def random_colour():
            try:
                col = [random.random() for a in range(3)]
                rng = sorted([int(random.random() * vert_num)  for a in range(2)])
                sel = xform.vtx[slice(*rng)]
                paint(sel, col)
                return True
            except pmc.MayaNodeError:
                pass
        while True:
            if not ex(random_colour): break
            time.sleep(1)
    pmc.select(clear=True)
    pmc.scriptJob(ro=True, ie=threading.Thread(target=flip).start)
