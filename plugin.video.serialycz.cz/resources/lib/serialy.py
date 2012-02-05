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
import urllib2,re,os,md5,sys
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util,resolver

__scriptid__   = 'plugin.video.serialycz.cz'
__scriptname__ = 'serialycz.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.serialycz.cz/'

def _get_meta(name,link):
	# load meta from disk or download it (slow for each serie, thatwhy we cache it)
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	m = md5.new()
	m.update(name)
	image = os.path.join(local,m.hexdigest()+'_img.url')
	plot = os.path.join(local,m.hexdigest()+'_plot.txt')
	if not os.path.exists(image):
		data = util.request(link)
		data = util.substr(data,'<div id=\"archive-posts\"','</div>')
		m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			data = util.request(m.group('url'))
			_get_image(data,image)
			_get_plot(data,plot)
	return _load(image).strip(),_load(plot)
	

def _save(data,local):
	print 'Saving file %s' % local
	f = open(local,'w')
	f.write(data)
	f.close()

def _load(file):
	if not os.path.exists(file):
		return ''
	f = open(file,'r')
	data = f.read()
	f.close()
	return data

def _get_plot(data,local):
 		data = util.substr(data,'<div class=\"entry-content\"','</p>')
		m = re.search('<(strong|b)>(?P<plot>(.+?))<', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			_save(util.decode_html(m.group('plot')).encode('utf-8'),local)
def _get_image(data,local):
 		data = util.substr(data,'<div class=\"entry-photo\"','</div>')
		m = re.search('<img(.+?)src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			_save(m.group('img'),local)
	
def list_series():
	data = util.substr(util.request(BASE_URL),'<div id=\"primary\"','</div>')
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	util.add_dir(__language__(30003),{'newest':'list'},util.icon('new.png'))
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
	for m in re.finditer(pattern, util.substr(data,'Seriály</a>','</ul>'), re.IGNORECASE | re.DOTALL):
		image,plot = _get_meta(m.group('name'),m.group('link'))
		util.add_dir(m.group('name'),{'serie':m.group('link')[len(BASE_URL):]},image,infoLabels={'Plot':plot})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_episodes(url):	
	data = util.request(BASE_URL+url)
	data = util.substr(data,'<div id=\"archive-posts\"','</div>')
	m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = util.request(m.group('url'))
		for m in re.finditer('<a href=\"(?P<link>[^\"]+)(.+?)(<strong>|<b>)(?P<name>[^<]+)', util.substr(data,'<div class=\"entry-content','</div>'), re.IGNORECASE | re.DOTALL):
			add_video(m.group('name'),m.group('link'))
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def newest_episodes():
	data = util.substr(util.request(BASE_URL+'category/new-episode/'),'<div id=\"archive-posts\"','</ul>')
	pattern='<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_video(m.group('name'),m.group('link'),m.group('img'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_video(name,url,image=''):
	return util.add_video(name,{'play':url},image,menuItems={xbmc.getLocalizedString(33003):{'name':name+'.mp4','download':url}})

def resolve(url):
	if not url.startswith('http'):
		url = BASE_URL+url
	data = util.substr(util.request(url),'<div id=\"content\"','#content')
	resolved = resolver.findstreams(__addon__,data,['<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
	if resolved == None:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
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
		util.download(__addon__,name,stream,os.path.join(downloads,name))

def handle(p):
	if p=={}:
		xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
		list_series()
	if 'newest' in p.keys():
		newest_episodes()
	if 'serie' in p.keys():
		list_episodes(p['serie'])
	if 'play' in p.keys():
		play(p['play'])
	if 'download' in p.keys():
		download(p['download'],p['name'])
