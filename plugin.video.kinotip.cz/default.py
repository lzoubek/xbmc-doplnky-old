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
import xbmcaddon,xbmc,xbmcplugin,os

__scriptid__   = 'plugin.video.kinotip.cz'
__scriptname__ = 'kinotip.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )
import filmy,divx
import util

divx.__addon__ = __addon__
divx.__language__ = __language__
filmy.__addon__ = __addon__
filmy.__language__ = __language__

def server(params):
	if params['server'] == 'filmy':
		return filmy.handle(params)
	if params['server'] == 'divx':
		return divx.handle(params)

def root():
	util.add_dir('Filmy',{'server':'filmy'})
	util.add_dir('DivX Filmy',{'server':'divx'})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

p = util.params()
if p=={}:
	root()
if 'server' in p.keys():
	server(p)
