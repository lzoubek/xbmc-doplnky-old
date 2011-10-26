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

_addon_ = None
_server_ = None
_base_url = None

def icon(icon):
	icon_file = os.path.join(_addon_.getAddonInfo('path'),'resources','icons',icon)
	if not os.path.isfile(icon_file):
		return 'DefaultFolder.png'
	return icon_file

def add_dir(name,params,logo='',infoLabels={}):
	params['server']=_server_
	if not logo == '':
		if logo.find('http') < 0 and not os.path.exists(logo):
			if logo[0] == '/':
				logo = logo[1:]
			logo = _base_url_+logo
	return util.add_dir(name,params,logo,infoLabels)

def add_stream(name,url,logo='',infoLabels={}):
	return util.add_video(
		name=name,
		params={'server':_server_,'play':url},
		logo=logo,
		infoLabels=infoLabels
	)

def _server_name_full(url):
	return re.search('http\://([^/]+)',url,re.IGNORECASE | re.DOTALL).group(1)
def _server_name(url):
	return re.search('/(.+?)\\.php',url,re.IGNORECASE | re.DOTALL).group(1)

def get_sources(data):
	data = util.substr(data,'<div class=\"content\"','<iframe src=\"http://www.facebook.com')
	sources = []
	for m in re.finditer('<embed(.+?)src=\"(?P<embed>[^\"]+)(.+?)</p>',data,re.IGNORECASE | re.DOTALL):
		sources.append([_server_name_full(m.group('embed')),m.group('embed')])
	for m in re.finditer('<a href=\"(?P<embed>(/servertip|/putlocker|/novamov|/videoweed|/shockshare|/divxstage|/movshare)[^\"]+)',data,re.IGNORECASE | re.DOTALL):
		sources.append([_server_name(m.group('embed')),m.group('embed')])
	for m in re.finditer('<iframe(.+?)src=\"(?P<embed>[^\"]+)',data,re.IGNORECASE | re.DOTALL):
		sources.append([_server_name_full(m.group('embed')),m.group('embed')])
	return sources

def list_sources(data):
	source = 1
	for s in get_sources(data):
		add_stream('Zdroj %d - %s' % (source,s[0]),s[1])
		source += 1

def play(base_name,url):
	if url.find('http') < 0:
		if url.find('/') == 0:
			url = url[1:]
		url = _base_url_+url
		data = util.request(url)
		m = re.search('<iframe(.+?)src=[\'\"](?P<url>(.+?))[\'\"]',data,re.IGNORECASE | re.DOTALL )
		if not m == None:
			url = m.group('url')
		n = re.search('<meta http\-equiv(.+?)url=(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL )
		if not n == None:
			url = n.group('url')
	streams = resolver.resolve(url)
	if streams == []:
		xbmcgui.Dialog().ok(base_name,_addon_.getLocalizedString(30001))
		return
	if not streams == None:
		print 'Sending %s to player' % streams
		li = xbmcgui.ListItem(path=streams[0],iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(base_name,_addon_.getLocalizedString(30002))

def get_searches(addon,server):
	return util.get_searches(addon,server)

def add_search(addon,server,search):
	maximum = 20
	try:
		maximum = int(addon.getSetting('keep-searches'))
	except:
		util.error('Unable to parse convert addon setting to number')
		pass
	return util.add_search(addon,server,search,maximum)
