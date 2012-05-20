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

import re,os,urllib
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util,resolver
import youtuberesolver as youtube

__scriptid__   = 'plugin.video.videacesky.cz'
__scriptname__ = 'videacesky.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.videacesky.cz/'


def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def categories():
#	util.add_dir(__addon__.getLocalizedString(30001),{'top':BASE_URL+'/videozebricky/poslednich-50-videi'},util.icon('new.png'))
	util.add_dir('Top 200',{'top':furl('/videozebricky/top-100')},util.icon('top.png'))
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
	data = util.request(BASE_URL)
	data = util.substr(data,'<ul id=\"headerMenu2\">','</ul>')
	pattern = '<a href=\"(?P<url>[^\"]+)(.+?)>(?P<name>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
		if m.group('url') == '/':
			continue
		util.add_dir(m.group('name'),{'cat':furl(m.group('url'))})

def list_top(page):
	data = util.substr(page,'<div class=\"postContent','</ul>')
	pattern = '<li>[^<]*<a href="(?P<url>[^\"]+)[^>]*>(?P<name>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
		util.add_video(
			m.group('name'),
			{'play':furl(m.group('url'))},
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':m.group('url')}}
		)

def list_content(page,url=BASE_URL):
	data = util.substr(page,'<div class=\"contentArea','<div class=\"pagination\">')
	pattern = '<h\d class=\"postTitle\"><a href=\"(?P<url>[^\"]+)(.+?)<span>(?P<name>[^<]+)</span></a>(.+?)<div class=\"postContent\">[^<]+<a[^>]+[^<]+<img src=\"(?P<img>[^\"]+)[^<]+</a>[^<]*<div class=\"obs\">[^>]+>(?P<plot>(.+?))</p>'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
		plot = re.sub('<br[^>]*>','',m.group('plot'))
		util.add_video(
			m.group('name'),
			{'play':furl(m.group('url'))},
			m.group('img'),
			infoLabels={'plot':plot},
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':furl(m.group('url'))}}
		)
	data = util.substr(page,'<div class=\"pagination\">','</div>')
	m = re.search('<li class=\"info\"><span>([^<]+)',data)
	n = re.search('<li class=\"prev\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)',data)
	k = re.search('<li class=\"next\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)',data)
	# replace last / + everyting till the end
	myurl = re.sub('\/[\w\-]+$','/',url)
	if not m == None:
		if not n == None:
			util.add_dir('%s - %s' % (m.group(1),n.group('name')),{'cat':myurl+n.group('url')})
		if not k == None:
			util.add_dir('%s - %s' % (m.group(1),k.group('name')),{'cat':myurl+k.group('url')})
	
def resolve(url):
	data = util.substr(util.request(url),'<div class=\"postContent\"','</div>')
	youtube.__eurl__ = 'http://www.videacesky.cz/wp-content/plugins/jw-player-plugin-for-wordpress/player.swf'
	resolved = resolver.findstreams(__addon__,data,['<iframe src=\"(?P<url>[^\"]+)','\;file=(?P<url>[^\&]+)'])
	print resolved
	if resolved == None:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30002))
		return
	if not resolved == {}:
		return resolved['url']

def play(url):
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/download')
		name+='.flv'
		util.download(__addon__,name,stream,os.path.join(downloads,name))

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	categories()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
if 'top' in p.keys():
	list_top(util.request(p['top']))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
if 'cat' in p.keys():
	list_content(util.request(p['cat']),p['cat'])
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
if 'play' in p.keys():
	play(p['play'])
if 'download' in p.keys():
	download(p['download'],p['name'])
