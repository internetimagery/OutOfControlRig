# Out of Control Rig!
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
import OutOfControlRig.has as has
import OutOfControlRig.tool as tool
import OutOfControlRig.cache as cache
import OutOfControlRig.track as track
import OutOfControlRig.colour as colour

class Control(object):
    """ Control the rig ... controllerlessly? """
    def __init__(s, geos):
        # Cache our mesh information
        s.geos = geos = dict((a, has.skin(a)) for a in geos) # Get skins
        s.cache_influence = cache.skin_influeces(b for a, b in geos.iteritems())
        s.cache_weights = cache.skin_weights(b for a, b in geos.iteritems())
        s.cache_all = ",".join("%s.vtx[0:]" % a for a in geos) # Everything!

        s.picker = picker = tool.Picker(kws=True) # Picker tool
        picker.whitelist = geos
        picker.callback_start.add(s.activate_rig)
        picker.callback_click.add(s.picked)
        picker.callback_drag.add(s.dragging)
        picker.callback_stop.add(s.deactivate_rig)
        track.Selection(kws=True).callback.add(s.selection_update) # Register our selection callback

    def selection_update(s, sel):
        """ Selection changes """
        num = len(sel) # Number of items selected
        if num == 1:
            sel = sel[0]
            if sel in s.geos: # Have we selected one of our meshes?
                s.picker.set()
                return
        # elif s.picker.active: s.picker.unset() # Clicked on nothing, clear picker

    def activate_rig(s):
        """ turn on our rig """
        colour.paint(s.cache_all) # Paint everything grey
        print "turning on rig"

    def deactivate_rig(s):
        """ turn off the rig """
        colour.paint(s.cache_all)
        colour.erase(s.geos) # Clear our colour information

    def picked(s, mesh, ID):
        """ making a selection """
        if mesh: # Did we pick something?
            print "PICKED", mesh, ID
        else:
            s.picker.unset()

    def dragging(s, mesh, ID):
        """ dragging selection """
        if mesh:
            print "Dragging", mesh, ID

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    Control([xform])
