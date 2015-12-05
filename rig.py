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

        track.Selection(kws=True).callback.add(s.selection_update) # Register our selection callback
        s.picker = tool.Picker()
        picker.whitelist = geos
        picker.callback_click.add(s.highlight_mesh)

    def selection_update(s, sel):
        """ Selection changes """
        num = len(sel) # Number of items selected
        if num == 1:
            sel = sel[0]
            if sel in s.geos: # Have we selected one of our meshes?
                s.activate_rig()
                return
        s.deactivate_rig()

    def activate_rig(s):
        """ turn on our rig """
        colour.paint(s.cache_all) # Paint everything grey
        s.picker.set()
        print "turning on rig"

    def deactivate_rig(s):
        """ turn off the rig """
        colour.paint(s.cache_all)
        colour.erase(s.geos) # Clear our colour information

    def highlight_mesh(s, mesh, ID):
        """ highlight the mesh """
        print mesh, ID
        pass

if __name__ == '__main__':
    # Testing
    pmc.system.newFile(force=True)
    xform, shape = pmc.polyCylinder() # Create a cylinder and joints
    jnt1, jnt2 = pmc.joint(p=(0,-1,0)), pmc.joint(p=(0,1,0))
    sk = pmc.skinCluster(jnt1, xform) # Bind them to the cylinder
    Control([xform])
