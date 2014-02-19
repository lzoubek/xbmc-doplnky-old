# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import os
sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )
import befun
import xbmcprovider,xbmcaddon,xbmcutil,xbmc,utmain
import util
import traceback,urllib2

__scriptid__   = 'plugin.video.befun.cz'
__scriptname__ = 'befun.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString
__set          = __addon__.getSetting

order_map = {'0':'','1':'inverse=0','2':'order=rating','3':'order=seen'}
order_by = order_map[__addon__.getSetting('order-by')]

settings = {'downloads':__set('downloads'),'quality':__set('quality'),'order-by':order_by,'strict-search':__set('strict-search'),'subs':__set('subs') == 'true'}

params = util.params()
if params=={}:
    xbmcutil.init_usage_reporting( __scriptid__)
provider = befun.BefunContentProvider()
provider.order_by = order_by
provider.strict_search = __addon__.getSetting('strict-search') == 'true'

class BefunXBMContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):

    def resolve(self,url):
        result = xbmcprovider.XBMCMultiResolverContentProvider.resolve(self,url)
        if result:
            # ping befun.cz GA account
            host = 'befun.cz'
            tc = 'UA-35173050-1'
            try:
                utmain.main({'id':__scriptid__,'host':host,'tc':tc,'action':url})
            except:
                print 'Error sending ping to GA'
                traceback.print_exc()
        return result

BefunXBMContentProvider(provider,settings,__addon__).run(params)
