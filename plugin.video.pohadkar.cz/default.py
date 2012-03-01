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

import re,os,urllib,urllib2,md5
import xbmcaddon,xbmc,xbmcgui,xbmcplugin

__scriptid__   = 'plugin.video.pohadkar.cz'
__scriptname__ = 'pohadkar.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )

import util,resolver,search
import youtuberesolver as youtube


BASE_URL='http://www.pohadkar.cz/'

def _search_cb(what):
	print 'searching for '+what

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def _get_meta(name,link):
	# load meta from disk or download it (slow for each tale, thatwhy we cache it)
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	m = md5.new()
	m.update(name)
	image = os.path.join(local,m.hexdigest()+'_img.png')
	plot = os.path.join(local,m.hexdigest()+'_plot.txt')
	if not os.path.exists(image):
		data = util.request(link)
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
 		data = util.substr(data,'<div id=\"tale_description\"','<div class=\"cleaner')
		p = data
		p = re.sub('<div[^>]+>','',p)
		p = re.sub('<table.*','',p)
		p = re.sub('</span>|<br[^>]*>|<ul>|</ul>|<hr[^>]*>','',p)
		p = re.sub('<span[^>]*>|<p[^>]*>|<li[^>]*>','',p)
		p = re.sub('<strong>|<a[^>]*>|<h[\d]+>','[B]',p)
		p = re.sub('</strong>|</a>|</h[\d]+>','[/B]',p)
		p = re.sub('</p>|</li>','[CR]',p)
		p = re.sub('<em>','[I]',p)
		p = re.sub('</em>','[/I]',p)
		p = re.sub('<img[^>]+>','',p)
		p = re.sub('\[B\]Edituj popis\[\/B\]','',p)
		p = re.sub('\[B\]\[B\]','[B]',p)
		p = re.sub('\[/B\]\[/B\]','[/B]',p)
		p = re.sub('\[B\][ ]*\[/B\]','',p)
		_save(util.decode_html(''.join(p)).encode('utf-8'),local)


def _get_image(data,local):
		m = re.search('<img id=\"tale_picture\" src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			img = furl(m.group('img'))
			print ' Downloading %s' % img
			_save(util.request(img),local)

def categories():
	#search.item()
	util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
	data = util.substr(util.request(BASE_URL),'<div class=\"vypis_data\"','</div')
	letters = ['A','B','C','Č','D','Ď','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','Ř','S','Š','T','Ť','U','V','W','X','Y','Z','Ž']
	for letter in letters:
		data = util.request(BASE_URL+'system/load-vypis/?znak='+letter+'&typ=1&zar=hp')
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			image,plot = _get_meta(m.group('name'),furl(m.group('url')))
			util.add_dir(m.group('name'),{'tale':furl(m.group('url')+'video/')},image,infoLabels={'Plot':plot})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def list_page(url):
	page = util.request(url)
	return parse_page(page,url)

def parse_page(page,url):
	data = util.substr(page,'<div class=\"vypis','<div class=\"right')
	pattern = '<div class=\"tale_char_div\"(.+?)<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<a(.+?)href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)<(.+?)<p[^>]*>(?P<plot>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		util.add_video(
			m.group('name'),
			{'play':furl(m.group('url'))},
			m.group('img'),
			infoLabels={'Plot':m.group('plot')},
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':furl(m.group('url'))}}
		)
	data = util.substr(page,'<p class=\"p_wrapper','</p>')
	index =  url.find('?')
	if index > 0:
		url = url[:index]
	n = re.search('<a(.+?)href=\"(?P<url>[^\"]+)\"[^>]*>&gt;<',data)
	if n:
		util.add_dir(__language__(30012),{'tale':furl(url+n.group('url'))},util.icon('next.png'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		if len(stream) > 1:
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			for st in stream:
				li = xbmcgui.ListItem(path=st,iconImage='DefaultVideo.png')
				playlist.add(st,li)
		li = xbmcgui.ListItem(path=stream[0],iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)

def resolve(url):
	page = util.request(url)
	data = util.substr(page,'<div id=\"video','<div id=\"controller')
	youtube.__eurl__ = url
	resolved = resolver.findstreams_multi(__addon__,data,['<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=\"(?P<url>[^\"]+)'])
	if resolved == None:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
		return
	if not resolved == []:
		return [r['url'] for r in resolved]

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/download')
		if len(stream) > 1:
			index=0
			for st in stream:
				index+=1
				filename = name+'_part'+str(index)
				if index == len(stream)-1:
					util.download(__addon__,filename,st,os.path.join(downloads,filename+'.mp4'))
				else:
					util.download(__addon__,filename,st,os.path.join(downloads,filename+'.mp4'),notifyFinishDialog=False)
		else:
			util.download(__addon__,name,stream[0],os.path.join(downloads,name+'.mp4'))

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	categories()
if 'tale' in p.keys():
	list_page(p['tale'])
if 'play' in p.keys():
	play(p['play'])
if 'download' in p.keys():
	download(p['download'],p['name'])
search.main(__addon__,'search_history',p,_search_cb)
