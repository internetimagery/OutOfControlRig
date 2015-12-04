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

import maya.cmds as cmds

POLY_VERTS = 31 # Filter Expand index

def skin_influeces(skins):
    """
    Given a list of skins, return a dict with cached verts
    cache = {joint : "mesh.vtx[ID]"}
    """
    cache = collections.defaultdict(list)
    for skin in skins:
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

def skin_weights(skins):
    """
    Given a list of skins, return a cache with mesh, face ID and highest ranking joint
    cache = {mesh: {ID: joint}}
    """
    cache = collections.defaultdict(dict)
    vert = "%s.vtx[%s]"
    for skin in skins:
        joints = skin.getInfluence() # Get joints affecting skin
        geos = skin.getGeometry() # Mesh affecting skin
        for geo in geos:
            for ID in range(geo.numFaces()): # Iterate through all faces
                verts = tuple(vert % (geo, a) for a in geo.getPolygonVertices(ID))
                weights = tuple(pmc.animation.skinPercent(str(skin), a, q=True, v=True) for a in verts)
                totals = {} # Record influences from joints
                for i, w in enumerate(zip(*weights)): # Loop through joints and weights
                    totals[sum(w) / len(verts)] = joints[i] # Identical weights pick joint at random
                highest_weight = totals[max(totals)]
                cache[geo][ID] = highest_weight # Record in our cache
    return cache

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    print skin_influeces([sk])
    print skin_weights([sk])
