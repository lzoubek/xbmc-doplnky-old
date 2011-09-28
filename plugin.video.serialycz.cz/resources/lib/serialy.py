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
	image = os.path.join(local,m.hexdigest()+'_img.png')
	plot = os.path.join(local,m.hexdigest()+'_plot.txt')
	if not os.path.exists(image):
		data = util.request(link)
		data = util.substr(data,'<div id=\"archive-posts\"','</div>')
		m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			data = util.request(m.group('url'))
			_get_image(data,image)
			_get_plot(data,plot)
	return image,_load(plot)
	

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
			print ' Downloading %s' % m.group('img')
			_save(util.request(m.group('img')),local)
	
def list_series():
	data = util.substr(util.request(BASE_URL),'<div id=\"primary\"','</div>')
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	util.add_dir(__language__(30003),{'newest':'list'},'')
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
			add_video(m.group('name'),m.group('link')[len(BASE_URL):])
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def newest_episodes():
	data = util.substr(util.request(BASE_URL+'category/new-episode/'),'<div id=\"archive-posts\"','</ul>')
	pattern='<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_video(m.group('name'),m.group('link')[len(BASE_URL):],m.group('img'))	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_video(name,url,image=''):
	return util.add_video(name,{'play':url},image)

def play(url):
	streams = None
	data = util.substr(util.request(BASE_URL+url),'<div id=\"content\"','<div id=\"sidebar')
	resolved = []
	matches = re.findall('<iframe(.+?)src=[\"\'](.+?)[\'\"]',data,re.IGNORECASE | re.DOTALL )
	matches.extend(re.findall('<object(.+?)data=\"([^\"]+)',data,re.IGNORECASE | re.DOTALL ))
	for m in matches:
		streams = resolver.resolve(m[-1])
		if not streams == None:
			resolved.extend(streams)
	if streams == []:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
		return
	if not resolved == []:
		stream = resolved[0]
		if len(resolved) > 1:
			dialog = xbmcgui.Dialog()
			ret = dialog.select(__language__(30004), resolved)
			if ret > 0:
				stream = resolved[ret]
			if ret < 0:
				return
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(__scriptname__,__language__(30002))

def handle(p):
	if p=={}:
		list_series()
	if 'newest' in p.keys():
		newest_episodes()
	if 'serie' in p.keys():
		list_episodes(p['serie'])
	if 'play' in p.keys():
		play(p['play'])
