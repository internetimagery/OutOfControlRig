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

def skin_influeces(skins):
    """ Given a list of skins, return a dict with cached verts """
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




# def skin_weights(skin):
#     """ Given a skin, return a dict with joints and cached weights """
#     cache = collections.defaultdict(collections.defaultdict(list))
#     geo = skin.getGeometry()
#     joints = skin.getInfluence()
#

# TODO: create a cache for all skin weights. {joint, mesh, [weight1, weight2]}
    # def pickSkeleton(s, mesh, faceID):
    #     """
    #     Pick a bone, given a skinned mesh and a face ID
    #     """
    #     # Get verts from Face
    #     meshes = s.meshes
    #     verts = [int(v) for v in findall(r"\s(\d+)\s", cmds.polyInfo("%s.f[%s]" % (mesh, faceID), fv=True)[0])]
    #
    #     weights = {}
    #     for joint in meshes[mesh]:
    #         weights[joint] = weights.get(joint, 0) # Initialize
    #         weights[joint] = sum([meshes[mesh][joint][v] for v in verts if v in meshes[mesh][joint]])
    #
    #     if weights:
    #         maxWeight = max(weights, key=lambda x: weights.get(x))
    #         return maxWeight

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    print skin_influeces([sk])
    print skin_weights([sk])
