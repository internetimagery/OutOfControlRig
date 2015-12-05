# Testing things

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

def SelectionList(name):
    sel = om.MSelectionList()
    sel.add(name)
    return sel

def MObject(name): return SelectionList(name).getDependNode(0)
def DagPath(name): return SelectionList(name).getDagPath(0)
def Plug(name): return SelectionList(name).getPlug(0)

print MObject("pSphere1")
loc = omui.MFnRotateManip()
