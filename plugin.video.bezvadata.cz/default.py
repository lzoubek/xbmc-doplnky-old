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

import re,os,urllib,urllib2
import xbmcaddon,xbmc,xbmcgui,xbmcplugin

__scriptid__   = 'plugin.video.bezvadata.cz'
__scriptname__ = 'bezvadata.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString


import util

import xbmcutil
import bezvadata


# filter function
def can_show(ext_filter,item):
	extension = os.path.splitext(item)[1]
	if extension in ext_filter:
		return False
	return True

def create_filter():
	ext_filter = __addon__.getSetting('ext-filter').split(',')
	return ['.'+f.strip() for f in ext_filter]

def filter(item):
	return can_show(create_filter(),item['title'])

provider = bezvadata.BezvadataContentProvider(filter=filter)

settings = {'downloads':__addon__.getSetting('downloads')}

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
XBMContentProvider(provider,settings).run(p)
#search.main(__addon__,'search_history',p,_search_cb)
