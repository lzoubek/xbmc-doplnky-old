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

import util,xbmcplugin,xbmcgui,xbmc,os,sys,re,resolver
import simplejson as json

def play(addon,base_name,base_url,url):
	print addon
	if url.find('http') < 0:
		if url.find('/') == 0:
			url = url[1:]
		url = base_url+url
		data = util.request(url)
		m = re.search('<iframe(.+?)src=[\'\"](?P<url>(.+?))[\'\"]',data,re.IGNORECASE | re.DOTALL )
		if not m == None:
			url = m.group('url')
	streams = resolver.resolve(url)
	if streams == []:
		xbmcgui.Dialog().ok(base_name,addon.getLocalizedString(30001))
		return
	if not streams == None:
		print 'Sending %s to player' % streams
		li = xbmcgui.ListItem(path=streams[0],iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(base_name,addon.getLocalizedString(30002))

def get_searches(addon,server):
	local = xbmc.translatePath(addon.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,server)
	if not os.path.exists(local):
		return []
	f = open(local,'r')
	data = f.read()
	searches = json.loads(unicode(data.decode('utf-8','ignore')))
	f.close()
	return searches

def add_search(addon,server,search):
	maximum = 20
	try:
		maximum = int(addon.getSetting('keep-searches'))
	except:
		util.error('Unable to parse convert addon setting to number')
		pass
	searches = []
	local = xbmc.translatePath(addon.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,server)
	if os.path.exists(local):
		f = open(local,'r')
		data = f.read()
		searches = json.loads(unicode(data.decode('utf-8','ignore')))
		f.close()
	searches.insert(0,search)
	remove = len(searches)-maximum
	if remove>0:
		for i in range(remove):
			searches.pop()
	f = open(local,'w')
	f.write(json.dumps(searches,ensure_ascii=True))
	f.close()
	



