# Ask questions about objects
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
import re

def skin(mesh):
    """ Query if mesh has a skin attached. If so return skin. """
    return pmc.mel.findRelatedSkinCluster(mesh) or None

def vert_ids(mesh, ID):
    """ Given mesh and face ID, return vert IDs associated with that """
    face = "%s.f[%s]" % (mesh, ID)
    reg = re.compile(r"\s(\d+)\s")
    return tuple(int(v) for v in reg.findall(pmc.polyInfo(face, fv=True)[0]))

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    assert skin(xform) == sk # Check for skin cluster
    assert vert_ids(xform, 1) == (1,2,22,21)
