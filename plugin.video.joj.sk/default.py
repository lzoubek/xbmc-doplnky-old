# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Maros Ondrasek
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
import joj
import xbmcprovider,xbmcaddon,xbmcutil,xbmc
import util
import traceback,urllib2

__scriptid__   = 'plugin.video.joj.sk'
__scriptname__ = 'joj.sk'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

settings = {'downloads':__addon__.getSetting('downloads'),'quality':__addon__.getSetting('quality')}
params = util.params()
if params=={}:
    xbmcutil.init_usage_reporting(__scriptid__)
provider = joj.JojContentProvider()

xbmcprovider.XBMCMultiResolverContentProvider(provider,settings,__addon__).run(params)
