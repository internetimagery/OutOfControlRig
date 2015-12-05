# Testing things

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds


def stuff():
    print "TOOL CHANGED"

cmds.scriptJob(e=["ToolChanged", stuff], ro=True)
cmds.scriptJob(e=["PostToolChanged", stuff], ro=True)
