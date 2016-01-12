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

import OutOfControlRig.tool as tool
import OutOfControlRig.collection as collection


class Rig(object):
    """ Rig!! """
    def __init__(s):
        s.tool = tool.Picker()
        # container = Meshes("OutOfControlRig")

    def get_meshes(s):
        """ Get meshes from the scene """


if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder(sy=5) # Create a cylinder and joints
    jnt1, jnt2, jnt3 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,0,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform, mi=1) # Bind them to the cylinder
    container = Meshes("OutOfControlRig")
    container.add([xform])
    pmc.select(clear=True)
    Rig()
