# Trackng Changes
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

import functools
import traceback
import contextlib
import pymel.core as pmc

@contextlib.contextmanager
def _print_exc():
    """ Print most recent exception. Useable in scripjob """
    try:
        yield
    except:
        print traceback.format_exc()
        raise

class Selection(object):
    """ Track changes to the current selection """
    job_args = set(("p","parent","rp","replacePrevious","kws","killWithScene","ro","runOnce","cu","compressUndo"))
    def __init__(s, **kwargs):
        job_args, s.callback = s.job_args, None
        # Initialize arguments for our job and list
        args = dict((a, kwargs.pop(a)) for a in kwargs.keys() if a in job_args)
        args["e"] = ("SelectionChanged", s._changed)
        kwargs["sl"] = True
        s.ls = ls = functools.partial(pmc.ls, **kwargs)
        s._last_selection = ls()
        s.id = pmc.scriptJob(**args)

    def _changed(s):
        """ Selection changed. Update everyone. """
        with _print_exc():
            sel = s.ls()
            if sel == s._last_selection: return
            s._last_selection, callback = sel, s.callback
            if callback: callback(sel)

    def kill(s): pmc.scriptJob(kill=s.id)

class Tool(object):
    """ Track changes to the current tool """
    def __init__(s, **kwargs):
        s.callback, s._last_tool = None, pmc.currentCtx()
        kwargs["e"] = ("PostToolChanged", s._changed)
        s.id = pmc.scriptJob(**kwargs)

    def _changed(s):
        """ Tool changed. Update everyone """
        with _print_exc():
            tool, callback = pmc.currentCtx(), s.callback
            if tool == s._last_tool: return
            s._last_tool = tool
            if callback: callback(tool)

    def kill(s): pmc.scriptJob(kill=s.id)

class Scene(object):
    """ Track changes to the scene (loading / new / etc) """
    def __init__(s, **kwargs):
        s.callback = None
        s.ids = ids = []
        kwargs["e"] = ("PostSceneRead", s._changed)
        ids.append(pmc.scriptJob(**kwargs))
        kwargs["e"] = ("NewSceneOpened", s._changed)
        ids.append(pmc.scriptJob(**kwargs))

    def _changed(s):
        """ Scene changed. Update everyone """
        with _print_exc():
            callback = s.callback
            scene = pmc.system.sceneName() or ""
            if callback: callback(scene)

    def kill(s): [pmc.scriptJob(kill=id_) for id_ in s.ids]


if __name__ == '__main__':
    #Test!
    def changed_selection(sel):
        print "Selection changed to:", sel
    def changed_tool(tool):
        print "Tool changed to:", tool
    def changed_scene(name):
        print "Scene changed to:", name
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder
    Selection(kws=True, type="transform").callback = changed_selection
    Tool(kws=True).callback = changed_tool
    Scene(ro=True).callback = changed_scene
