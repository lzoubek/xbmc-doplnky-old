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

import util,xbmcplugin,xbmcgui,sys,re,resolver

def play(base_name,base_url,url):
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
		xbmcgui.Dialog().ok(base_name,'Video neni dostupne, zkontrolujte,[CR]zda funguje na webu')
		return
	if not streams == None:
		print 'Sending %s to player' % streams
		li = xbmcgui.ListItem(path=streams[0],iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(base_name,'Prehravani vybraneho videa z tohoto zdroje[CR]zatim neni podporovano.')

