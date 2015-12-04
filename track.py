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
        s.callbacks = set()
        s.job_id = pmc.scriptJob(e=["SelectionChanged", s._changed], **kwargs)
    def _changed(s):
        """ Selection changed. Update everyone. """
        sel = pmc.ls(sl=True)
        try:
            for caller in s.callbacks:
                caller(sel)
        except:
            print traceback.format_exc()
            raise
    def register(s, func):
        """ Register callbacks for event """
        s.callbacks.add(func)
    def remove(s, func):
        """ Remove callback from event """
        s.callbacks.discard(func)
    def kill(s):
        """ Stop watching the event """
        pmc.scriptJob(kill=s.job_id)

if __name__ == '__main__':
    #Test!
    def changed(sel):
        print "Selection changed to:", sel
    tracker = Selection(ro=True)
    tracker.register(changed)
