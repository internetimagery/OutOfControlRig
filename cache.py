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
import maya.api.OpenMaya as om
from collections import defaultdict as dd

class Geo_Cache(dict):
    """ Map vertices to faces """
    def __missing__(s, mesh):
        vert_map = dd(list)
        try:
            offset, verts = mesh.getVertices()
            faces = (d for c in ((a,)*b for a, b in enumerate(offset)) for d in c)
            for vert, face in zip(verts, faces):
                vert_map[vert].append(face)
        except AttributeError:
            print "Invalid mesh, %s" % mesh
        dict.__setitem__(s, mesh, vert_map)
        return vert_map

def preferred_joint_and_influence(meshes):
    """
    Given a list of meshes. Cache joint influences and preferred joints
    cache_inf = {joint: influence}
    cache_pref = {mesh: {faceID: joint}}
    """
    mesh_map = Geo_Cache()
    influence = dd(list)
    totals = dd(lambda: dd(dict))

    for skin in (pmc.mel.findRelatedSkinCluster(a) for a in meshes):
        if skin:
            skin = pmc.PyNode(skin)
            joints = skin.getInfluence() # Get joints

            for jnt in joints: # Loop joints to get influences etc
                influences, weights = skin.getPointsAffectedByInfluence(jnt)
                for inf in influences: # A list for some reason...
                    influence[jnt].append(inf) # Quick! Cache influence of joint

                    mesh = inf.node()
                    for vert, weight in zip(inf.indicesIter(), weights): # Loop our verts
                        for face in mesh_map[mesh][vert]:
                            totals[mesh][face][weight] = jnt

    sel = pmc.ls(sl=True)
    cache_inf = dict(pmc.select(b, r=True) or (a, tuple(pmc.PyNode(c) for c in pmc.filterExpand(ex=False, sm=31))) for a, b in influence.iteritems())
    pmc.select(sel, r=True)

    cache_pref = dict((a, dict((c, d[max(d)]) for c, d in b.iteritems())) for a, b in totals.iteritems())

    return cache_inf, cache_pref


if __name__ == '__main__':
    # Testing
    from pprint import pprint as pp
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder(sy=5) # Create a cylinder and joints
    jnts = [pmc.joint(p=a) for a in ((0,-1,0),(0,0,0),(0,1,0))]
    sk = pmc.skinCluster(jnts[0], xform, mi=2) # Bind them to the cylinder

    inf, pref = preferred_joint_and_influence([xform])
    print "Influence".center(20, "-")
    pp(inf)
    print "Preference".center(20, "-")
    pp(pref)
