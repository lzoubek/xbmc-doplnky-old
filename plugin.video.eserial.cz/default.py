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
import xbmcaddon,xbmc,xbmcgui,xbmcplugin,util,resolver,search

__scriptid__   = 'plugin.video.eserial.cz'
__scriptname__ = 'eserial.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.eserial.cz/'

def _search_cb(what):
	return list(BASE_URL+'hledej?hledej='+urllib.quote(what))

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def root():
	#search.item()
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
	data = util.request(BASE_URL)
	data = util.substr(data,'<div id=\"stred','<div id=\'patka>')
	for m in re.finditer('<a href=\'(?P<url>[^\']+)[^<]+<img src=\'(?P<img>[^\']+)[^<]+</a>[^<]*<br[^<]*<a[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
		util.add_dir(m.group('name'),{'show':m.group('url')},furl(m.group('img')))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show(url):
	data = util.request(furl(url))
	data = util.substr(data,'<menu>','</menu>')
	for m in re.finditer('<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
		util.add_dir(m.group('name'),{'list':url+m.group('url')})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list(url):
	url = furl(url)
	return list_page(util.request(url),url)

def list_page(data,url):
	for m in re.finditer('<div class=\'dily-vypis\'>(?P<show>.+?)<script>',data,re.IGNORECASE | re.DOTALL ):
		show = m.group('show')
		link = re.search('<a href=\'(?P<url>[^\']+)[^<]+<img src=\'(?P<img>[^\']+)[^<]+</a>[^<]*<br[^<]*<a[^>]+>(?P<index>[^<]+)<b>(?P<name>[^<]+)',show)
		if link:
			vurl = re.sub('\?.*','',url)+link.group('url')
			name = link.group('index') + link.group('name')
			util.add_video(
				name,
				{'play':vurl},
				logo=furl(link.group('img')),
				infoLabels={'Title':name},
				menuItems={xbmc.getLocalizedString(33003):{'name':name,'download':vurl}}
			)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def resolve(url):
	util.init_urllib()
	data = util.request(furl(url))	
	data = util.substr(data,'<div id=\"stred','<div id=\'patka>')
	resolved = resolver.findstreams(__addon__,data,['<embed( )*flashvars=\"file=(?P<url>[^\"]+)','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
	print resolved
	if resolved == None:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
		return
	if not resolved == {}:
		return resolved['url']
	xbmcgui.Dialog().ok(__scriptname__,__language__(30001))

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream = resolve(url)
	if stream:
		name+='.mp4'
		util.reportUsage(__scriptid__,__scriptid__+'/download')
		util.download(__addon__,name,stream,os.path.join(downloads,name))

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	root()
if 'show' in p.keys():
	show(p['show'])
if 'list' in p.keys():
	list(p['list'])
if 'play' in p.keys():
	play(p['play'])
if 'download' in p.keys():
	download(p['download'],p['name'])
#search.main(__addon__,'search_history',p,_search_cb)
