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

POLY_VERTS = 31 # Filter Expand index


class Cache(object):
    """ Cache of objects for quick lookup """
    def __init__(s, meshes):
        pass


# OpenMaya.MFnMesh.getFaceVertexIndex


def _map_vertices_to_faces(mesh):
    """ Map vert indices to faces """
    try:
        face_offset, vert_index = mesh.getVertices()
        face_index = (d for c in ((a,)*b for a, b in enumerate(face_offset)) for d in c)
        vert_to_face = dd(list) # Associate faces and vertices
        for vert, face in zip(vert_index, face_index):
            vert_to_face[vert].append(face)
        return vert_to_face
    except AttributeError as e:
        print "Invalid mesh", mesh, e

def skins(): # Hoover up all skins in the scene
    """
    Cache all joint and skin info in the scene
    cache1 = {mesh: {faceID: joint}}
    cache2 = {joint: vertices}
    """
    skins = pmc.ls(type="skinCluster")
    cache1 = dd(dict) # preferred joint per face
    cache2 = dd(list) # joints influence
    vert_to_face = {} # vert to face mapping
    for skin in skins:
        joints = skin.getInfluence() # Get affecting joints
        geos = skin.getGeometry() # Get meshes
        for geo in geos: # Associate verts with faces
            if geo not in vert_to_face:
                vert_to_face[geo] = _map_vertices_to_faces(geo) or []

        totals = dd(lambda: dd(lambda: dd(list))) # work out highest influence per face
        for joint in joints: # This seems to run much faster
            influence_list, weights = skin.getPointsAffectedByInfluence(joint)
            for influence in influence_list: # A list populated by one item? Ugh...
                cache2[joint].append(influence) # Add influence to the joint
                geo = influence.node() # Get mesh

                for vert, weight in zip(influence.indicesIter(), weights): # Loop our verts
                    for face in vert_to_face[geo][vert]:
                        totals[geo][face][joint].append(weight)

        # Caculate highest influence
        for geo, faces in totals.iteritems():
            for face, joints in faces.iteritems():
                summed = dict((sum(b) / len(b), a) for a, b in joints.iteritems())
                joint = summed[max(summed)] # Highest influence
                cache1[geo][face] = joint

    for joint, influence in cache2.iteritems(): # slim down to a single call
        pmc.select(influence, r=True)
        cache2[joint] = pmc.filterExpand(ex=False, sm=POLY_VERTS)
    return cache1, cache2

def skin_influeces(skins):
    """
    Given a list of skins, return a dict with cached verts
    cache = {joint : "mesh.vtx[ID]"}
    """
    cache = dd(list)
    for skin in skins:
        joints = skin.getInfluence() # Get joints affecting skin
        for joint in joints:
            pmc.select(clear=True)
            skin.selectInfluenceVerts(joint) # Select verts associated with joint
            for vert in pmc.filterExpand(sm=POLY_VERTS) or []: # Pull out each vertex
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
    cache = dd(dict)
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
    jnt1, jnt2, jnt3 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,0,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform, mi=2) # Bind them to the cylinder

    print skins()
    # print skin_influeces([sk])
    # print skin_weights([sk])
