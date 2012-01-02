
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
import os,re,sys
import xbmcplugin,xbmcaddon,xbmc
import util

def _list(addon,history):
	util.add_dir(util.__lang__(30004),{'search':''},util.icon('search.png'))
	for what in util.get_searches(addon,history):
		util.add_dir(what,{'search':what},menuItems={xbmc.getLocalizedString(117):{'search-remove':what}})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def _remove(addon,history,search):
	util.remove_search(addon,history,search)
	xbmc.executebuiltin('Container.Refresh')

def _search(addon,history,what,callback):
	if what == '':
		kb = xbmc.Keyboard('',util.__lang__(30003),False)
		kb.doModal()
		if kb.isConfirmed():
			what = kb.getText()
	if not what == '':
		maximum = 20
		try:
			maximum = int(addon.getSetting('keep-searches'))
		except:
			util.error('Unable to parse convert addon setting to number')
			pass

		util.add_search(addon,history,what,maximum)
		callback(what)
def item(items={}):
	items['search-list'] = ''
	util.add_dir(util.__lang__(30003),items,util.icon('search.png'))

def main(addon,history,p,callback):
	if 'search-list' in p.keys():
		_list(addon,history)
	if 'search' in p.keys():
		_search(addon,history,p['search'],callback)
	if 'search-remove' in p.keys():
		_remove(addon,history,p['search-remove'])
