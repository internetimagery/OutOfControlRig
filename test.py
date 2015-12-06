# Testing things

import maya.OpenMaya as old_om
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pmc

def MObject(name):
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDependNode(0)

pmc.system.newFile(force=True)
xform, shape = pmc.polyCylinder(sy=5) # Create a cylinder and joints
jnt1, jnt2, jnt3 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,0,0)), pmc.joint(p=(0,1,0))
sk = pmc.skinCluster(jnt1, xform, mi=1) # Bind them to the cylinder

sel = om.MSelectionList()
sel.add(str(sk.weightList))
plug = sel.getPlug(0)
