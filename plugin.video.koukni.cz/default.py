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
import xbmcaddon,xbmc,xbmcgui,xbmcplugin,util,search,resolver

__scriptid__   = 'plugin.video.koukni.cz'
__scriptname__ = 'koukni.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://koukni.cz/'

def _search_cb(what):
	return list(BASE_URL+'hledej?hledej='+urllib.quote(what))

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def root():
	search.item()
	util.add_dir(__language__(30010),{'list':furl('new')},util.icon('new.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
	util.add_dir(__language__(30011),{'list':furl('nej')},util.icon('top.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
	tags = util.get_searches(__addon__,'tags')
	if tags == []:
		# add default/known tags
		tags = ['clipz','simpsons','serialz','znovy','zoufalky','vypravej','topgear','COWCOOSH']
		for t in tags:
			util.add_search(__addon__,'tags',t,9999)
	tags.sort()
	for tag in tags:
		util.add_dir(tag,{'list':furl(tag)},menuItems={
		__addon__.getLocalizedString(30005):{'tag-add':''},
		__addon__.getLocalizedString(30006):{'tag-remove':tag}
		})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def tag_remove(tag):
	util.remove_search(__addon__,'tags',tag)
	xbmc.executebuiltin('Container.Refresh')

def tag_add():
	kb = xbmc.Keyboard('',__language__(30003),False)
	kb.doModal()
	if kb.isConfirmed():
			what = kb.getText()
			util.add_search(__addon__,'tags',what,9999)
			xbmc.executebuiltin('Container.Refresh')

def list(url):
	return list_page(util.request(url),url)

def list_page(data,url):
	for m in re.finditer('<div class=\"row\"(.+?)<a href=\"(?P<url>[^\"]+)(.+?)src=\"(?P<logo>[^\"]+)(.+?)<h1>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
		iurl = furl(m.group('url'))
		util.add_video(m.group('name'),
			{'play':iurl},
			logo=furl(m.group('logo')),
			infoLabels={'Title':m.group('name')},
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
			)
	prev = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/predchozi.png',data,re.IGNORECASE | re.DOTALL )
	navurl = url
	index = url.find('?')
	if index > 0:
		navurl = url[:index]
	if prev:
		print prev.group('url')
		util.add_dir(__addon__.getLocalizedString(30007),{'list':navurl+prev.group('url')},util.icon('prev.png'))
	next = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/dalsi.png',data,re.IGNORECASE | re.DOTALL )
	if next:
		print next.group('url')
		util.add_dir(__addon__.getLocalizedString(30008),{'list':navurl+next.group('url')},util.icon('next.png'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	stream,subs = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
		util.load_subtitles(subs)

def resolve(url):
	streams = resolver.resolve2(url)
	if len(streams)>0:
		return (streams[0]['url'],streams[0]['subs'])
	xbmcgui.Dialog().ok(__scriptname__,__language__(30001))

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream,subs = resolve(url)
	if stream:
		if not subs == '':
			util.save_to_file(subs,os.path.join(downloads,name+'.srt'))
		name+='.mp4'
		util.reportUsage(__scriptid__,__scriptid__+'/download')
		util.download(__addon__,name,stream,os.path.join(downloads,name))

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	root()
if 'list' in p.keys():
	list(p['list'])
if 'play' in p.keys():
	play(p['play'])
if 'download' in p.keys():
	download(p['download'],p['name'])
if 'tag-remove' in p.keys():
	tag_remove(p['tag-remove'])
if 'tag-add' in p.keys():
	tag_add()
search.main(__addon__,'search_history',p,_search_cb)
