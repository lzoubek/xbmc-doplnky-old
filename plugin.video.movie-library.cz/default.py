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

__scriptid__   = 'plugin.video.movie-library.cz'
__scriptname__ = 'movie-library.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )

import util,ulozto

BASE_URL='http://movie-library.cz/'

def icon(icon):
	icon_file = os.path.join(__addon__.getAddonInfo('path'),'resources','icons',icon)
	if not os.path.isfile(icon_file):
		return 'DefaultFolder.png'
	return icon_file

def search(what):
	if what == '':
		kb = xbmc.Keyboard('',__language__(30003),False)
		kb.doModal()
		if kb.isConfirmed():
			what = kb.getText()
	if not what == '':
		maximum = 20
		try:
			maximum = int(__addon__.getSetting('keep-searches'))
		except:
			util.error('Unable to parse convert addon setting to number')
			pass

		util.add_search(__addon__,'search_history',what,maximum)
		req = urllib2.Request(BASE_URL+'search.php?q='+what.replace(' ','+')+orderby())
		response = urllib2.urlopen(req)
		data = response.read()
		response.close()
		if response.geturl().find('search.php') > -1:
			return parse_page(data,response.geturl())
		else:
			#single movie was found
			return parse_item(data)
def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def search_list():
	util.add_dir(__language__(30004),{'search':''},icon('search.png'))
	for what in util.get_searches(__addon__,'search_history'):
		util.add_dir(what,{'search':what})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def categories():
	util.add_dir(__language__(30003),{'search-list':''},icon('search.png'))
	data = util.substr(util.request(BASE_URL),'div id=\"menu\"','</td')
	pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		util.add_dir(m.group('name'),{'cat':furl(m.group('url'))})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_page(url):
	order = orderby()
	if url.find('?') < 0:
		order = '?'+order
	url +=order
	page = util.request(url)
	return parse_page(page,url)

def parse_page(page,url):
	data = util.substr(page,'<div class=\"sortlist','<div class=\"pagelist')
	pattern = '<tr><td[^>]+><a href=\"(?P<url>[^\"]+)[^>]+><img src=\"(?P<logo>[^\"]+)(.+?)<a class=\"movietitle\"[^>]+>(?P<name>[^<]+)</a>(?P<data>.+?)/td></tr>'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		info = m.group('data')
		year = ''
		plot = ''
		genre = ''
		cz = ''
		rating = 0
		if re.search('^<img',info):
			cz = ' [cz]'
		s  = re.search('(.*?)<br />(<div(.+?)</div></div>)?(?P<genre>.*?)<br />(?P<year>.*?)<br />(?P<plot>[^<]+)',info)
		if s:
			genre = s.group('genre')
			try:
				year = int(re.sub(',.*','',s.group('year')))
			except:
				pass
			plot = s.group('plot')
		r = re.search('<div class=\"ratingval\"(.+?)width:(?P<rating>\d+)px',info)
		if r:
			try:
				rating = float(int(r.group('rating'))/5)
			except:
				pass
		util.add_dir(m.group('name')+cz,{'item':furl(m.group('url'))},m.group('logo'),infoLabels={'Plot':plot,'Genre':genre,'Rating':rating,'Year':year})
	navurl = url
	index = url.find('?')
	if index > 0:
		navurl = url[:index]
	data = util.substr(page,'setPagePos(\'curpage2\')','</div>')
	for m in re.finditer('<a(.+?)href=\"(.+?)(?P<page>page=\d+)[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL):
		logo = 'DefaultFolder.png'
		if m.group('name').find('Další') >= 0:
			logo = icon('next.png')
		if m.group('name').find('Předchozí') >= 0:
			logo = icon('prev.png')
		util.add_dir(m.group('name'),{'cat':navurl+'?'+m.group('page')},logo)

	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def orderby():
	return '&sort=%s' % __addon__.getSetting('order-by')

def list_item(url):
	return parse_item(util.request(url),url)

def parse_item(page,url):
	#search for series items
	print url
	data = util.substr(page,'Download:</h3><table>','</table>')
	pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a></div></td><td[^>]+>(?P<size>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		iurl = furl(m.group('url'))
		util.add_video('%s (%s)'%(m.group('name'), m.group('size')),
		{'play':iurl},
		menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
		)

	# search for movie items
	data = util.substr(page,'Download:</h3>','<div id=\"login-password-box')
	pattern = '<a class=\"under\" href="(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a></abbr></div><div[^>]+>(?P<size>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		iurl = furl(m.group('url'))
		util.add_video('%s (%s)'%(m.group('name'), m.group('size')),
		{'play':iurl},
		menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
		)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	stream = resolve(url)
	if stream:
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def resolve(url):
	data = util.request(url)
	# find uloz.to url
	m = re.search('window\.location=\'(?P<url>[^\']+)',data,re.IGNORECASE | re.DOTALL)
	if m:
		stream = ulozto.url(m.group('url'))
		if stream == -1:
			xbmcgui.Dialog().ok(__scriptname__,__language__(30002))
			return
		if stream == -2:
			xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
			return
		return stream
	else:
		# daily maximum of requested movies reached (150)
		util.error('daily maximum (150) requests for movie was reached, try it tomorrow')
#		m = re.search('javascript\" src=\"(?P<js>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
#		if m:
#			js = util.request(m.group('js'))
#			challenge = re.search('challenge :[^\']+\'([^\']+)',js,re.IGNORECASE|re.DOTALL).group(1)
#			dialog = xbmcgui.Dialog()
#			dialog.ok(__scriptname__,'ahoj','ahoj')
#			xbmc.executebuiltin('XBMC.Notification(%s,%s,10000,%s)' % (__scriptname__,'','http://www.google.com/recaptcha/api/image?c='+challenge))
#			kb = xbmc.Keyboard('','opis obrazek',False)
#			kb.doModal()
#			if kb.isConfirmed():
#				code = kb.getText()

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream = resolve(url)
	if stream:
		localfile = os.path.join(downloads,xbmc.makeLegalFilename(name))
		util.download(__addon__,name,stream,localfile)

p = util.params()
if p=={}:
	categories()
if 'cat' in p.keys():
	list_page(p['cat'])
if 'item' in p.keys():
	list_item(p['item'])
if 'play' in p.keys():
	play(p['play'])
if 'download' in p.keys():
	download(p['download'],p['name'])
if 'search-list' in p.keys():
	search_list()
if 'search' in p.keys():
	search(p['search'])
