# Generate useful cache information.
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
import collections

POLY_VERTS = 31 # Filter Expand index

def skin(skins):
    """ Given a list of skins, return a dict with cached verts """
    cache = collections.defaultdict(list)
    for skin in skins:
        skin = pmc.PyNode(skin) # Nodify the skin string
        joints = skin.getInfluence() # Get joints affecting skin
        for joint in joints:
            pmc.select(clear=True)
            skin.selectInfluenceVerts(joint) # Select verts associated with joint
            for vert in pmc.filterExpand(sm=POLY_VERTS): # Pull out each vertex
                influences = pmc.animation.skinPercent(skin, vert, q=True, v=True)
                for i, influence in enumerate(influences):
                    if 0.2 < influence: # Trim tiny influences.
                        cache[joints[i]].append(vert) # Add to cache
    for joint in cache:
        pmc.select(cache[joint], r=True)
        cache[joint] = pmc.filterExpand(ex=False, sm=POLY_VERTS) # Reduce calls
    return cache

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    print skin([sk])
