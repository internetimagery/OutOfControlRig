# Trackng Selection Changes
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

import traceback
import pymel.core as pmc

class Selection(object):
    """ Track changes to the current selection """
    def __init__(s, **kwargs):
        s.callback = set()
        s._last_selection = None
        s._job_id = pmc.scriptJob(e=("SelectionChanged", s._changed), **kwargs)
    def _changed(s):
        """ Selection changed. Update everyone. """
        sel = pmc.ls(sl=True)
        if sel == s._last_selection: return
        s._last_selection = sel
        try:
            for caller in s.callback:
                caller(sel)
        except:
            print traceback.format_exc()
            raise
    def kill(s):
        """ Stop watching the event """
        pmc.scriptJob(kill=s._job_id)
    def __del__(s): s.kill()

class Tool(object):
    """ Track changes to the current tool """
    def __init__(s, **kwargs):
        s.callback = set()
        s._last_tool = None
        s._job_id = pmc.scriptJob(e=("PostToolChanged", s._changed), **kwargs)
    def _changed(s):
        """ Tool changed. Update everyone """
        tool = pmc.currentCtx()
        if tool == s._last_tool: return
        s._last_tool = tool
        try:
            for caller in s.callback:
                caller(tool)
        except:
            print traceback.format_exc()
            raise

if __name__ == '__main__':
    #Test!
    def changed_selection(sel):
        print "Selection changed to:", sel
    def changed_tool(tool):
        print "Tool changed to:", tool
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    s = Selection(kws=True)
    s.callback.add(changed_selection)
    t = Tool(kws=True)
    t.callback.add(changed_tool)
