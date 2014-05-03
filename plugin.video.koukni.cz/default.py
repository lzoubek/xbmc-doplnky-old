# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Libor Zoubek
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

import re,os,urllib,urllib2,shutil,traceback
import xbmcaddon,xbmc,xbmcgui,xbmcplugin,xbmcutil,util

sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )

import xbmcprovider,koukni

__scriptid__   = 'plugin.video.koukni.cz'
__scriptname__ = 'koukni.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

settings = {'downloads':__addon__.getSetting('downloads'),'quality':__addon__.getSetting('quality')}

params = util.params()
if params=={}:
    xbmcutil.init_usage_reporting( __scriptid__)
xbmcprovider.XBMCMultiResolverContentProvider(koukni.KoukniContentProvider(),settings,__addon__).run(params)
