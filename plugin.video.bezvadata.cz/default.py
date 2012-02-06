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


import util,search


BASE_URL='http://bezvadata.cz/'

def _search_cb(what):
	url = BASE_URL+'vyhledavani/?s='+what.replace(' ','+')
	page = util.request(url)
	return parse_page(page)

def parse_page(page):
	
	ad = re.search('<a href=\"(?P<url>/vyhledavani/souhlas-zavadny-obsah[^\"]+)',page,re.IGNORECASE|re.DOTALL)
	if ad and __addon__.getSetting('18+content') == 'true':
		page = util.request(furl(ad.group('url')))
	data = util.substr(page,'<div class=\"content','<div class=\"stats')
	pattern = '<section class=\"img[^<]+<a href=\"(?P<url>[^\"]+)(.+?)<img src=\"(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+)(.+?)<b>velikost:</b>(?P<size>[^<]+)'
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		iurl = furl(m.group('url'))
		name = '%s (%s)' %(m.group('name'),m.group('size').strip())
		util.add_video(
			name,
			{'play':iurl},m.group('img'),
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
		)
	data = util.substr(page,'<div class=\"pagination','</div>')
	m = re.search('<li class=\"previous[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
	if m:
		util.add_dir(__language__(30011),{'list':furl(m.group('url'))})
	n = re.search('<li class=\"next[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
	if n:
		util.add_dir(__language__(30012),{'list':furl(n.group('url'))})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def categories():
	search.item()
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
	data = util.substr(util.request(BASE_URL),'div class=\"stats\"','<footer')
	pattern = '<section class=\"(?P<section>[^\"]+)(.+?)<h3>(?P<name>[^<]+)'
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		util.add_dir(m.group('name'),{'stats':m.group('section')})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def stats(section):
	data = util.substr(util.request(BASE_URL),'section class=\"'+section+'\"','</section')
	pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		iurl = furl(m.group('url'))
		print iurl
		util.add_video(m.group('name'),{'play':iurl})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def play(url):
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def resolve(url):
	data = util.request(url)
	request = urllib.urlencode({'stahnoutSoubor':'Stáhnout'})
	req = urllib2.Request(url+'?do=stahnoutForm-submit',request)
	req.add_header('User-Agent',util.UA)	
	resp = urllib2.urlopen(req)
	return resp.geturl()

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/download')
		util.download(__addon__,name,stream,os.path.join(downloads,name))

p = util.params()
util.init_urllib()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	categories()
if 'stats' in p.keys():
	stats(p['stats'])
if 'play' in p.keys():
	play(p['play'])
if 'list' in p.keys():
	parse_page(util.request(p['list']))
if 'download' in p.keys():
	download(p['download'],p['name'])
search.main(__addon__,'search_history',p,_search_cb)
