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

import re,os,urllib,urllib2,md5,traceback
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
__scriptid__   = 'plugin.video.csfd-trailers'
__scriptname__ = 'ČSFD Trailery'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer

__cache__ = StorageServer.StorageServer(__scriptid__, 1)

import scrapper

scrapper.__cache__ = __cache__
import util,resolver,search

BASE_URL='http://www.csfd.cz/'

def _search_cb(what):
	print 'searching for '+what

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL+url

def play(url):
	stream,subs = resolve(url)
	if stream:
		util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
		if not subs == 'null':
			player = xbmc.Player()
			count = 0
			max_count = 99
			while not player.isPlaying() and count < max_count:
				xbmc.sleep(200)
				count+=1
				if count < max_count:
					player.setSubtitles(subs)

def resolve(url):
	page = util.request(url)
	data = util.substr(page,'<div class=\"ui-video-player','</script')
	clip = re.search('player\.addClip\(\"(?P<url>[^\"]+).+?subtitles\":\"?(?P<subs>[^(}|\")]+)',data)
	if clip:
		stream = clip.group('url').replace('\\','')
		subs = clip.group('subs').replace('\\','')
		return stream,subs
	return None,'null'
		

def download(url,name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
		return
	stream,subs = resolve(url)
	if stream:
		print 'downloading...'

def root():
	util.add_dir('Kino',{'kino':'s'})
	#util.add_dir('Blue-ray',{'cat':'dvd','url':'http://www.csfd.cz/dvd-a-bluray/mesicne/'})
	#util.add_dir('Premiova DVD',{'cat':'dvd','url':'http://www.csfd.cz/dvd-a-bluray/mesicne/?format=dvd_retail'})
	#util.add_dir('Levna DVD',{'cat':'dvd','url':'http://www.csfd.cz/dvd-a-bluray/mesicne/?format=dvd_lite'})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def add_item(name,info):
	xbmc_info = scrapper.xbmc_info(info)
	util.add_dir(name,{'item':furl(info['url'])},info['img'],infoLabels=xbmc_info,menuItems={__language__(30007):'Action(info)'})

def kino(params):
	if 'kino-year' in params.keys() and 'kino-country' in params.keys():
		return kino_list('kino/prehled/?country=%s&year=%s' % (params['kino-country'],params['kino-year']))
	if 'kino-country' in params.keys():
		data = util.request(furl('kino/prehled'))
		data = util.substr(data,'id=\"frmfilter-year','</select>')
		for m in re.finditer('<option value=\"(?P<value>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			params['kino-year'] = m.group('value')
			util.add_dir(m.group('name'),params)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
	else:
		data = util.request(furl('kino/prehled'))
		data = util.substr(data,'id=\"frmfilter-country','</select>')
		for m in re.finditer('<option value=\"(?P<value>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			params['kino-country'] = m.group('value')
			util.add_dir(m.group('name'),params)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def kino_list(url):
	use_cache= __addon__.getSetting('cache-meta') == 'true'
	page = util.request(furl(url))
	data = util.substr(page,'<div id=\"releases\"','<div class=\"footer\">')
	for m in re.finditer('<td class=\"date\">(?P<date>[^<]+).+?<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+).+?<span class=\"film-year\">(?P<year>[^<]+)',data,re.IGNORECASE|re.DOTALL):
		if use_cache:
			info = scrapper.get_info(furl(m.group('url')))
			name = '%s %s %s %s' % (m.group('date'),m.group('name'),m.group('year'),info['percent'])
			add_item(name,info)
		else:
			info = scrapper._empty_info()
			info['url'] = m.group('url')
			name = '%s %s %s' % (m.group('date'),m.group('name'),m.group('year'))
			add_item(name,info)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def item(params):
	info = scrapper.get_info(params['item'])
	xbmc_info = scrapper.xbmc_info(info)
	page = util.request(info['url']+'/videa')
	data = util.substr(page,'<label for=\"frmfilterSelectForm-filter\">','</select>')
	util.add_dir(__language__(30007),params,info['img'],infoLabels=xbmc_info,menuItems={__language__(30007):'Action(info)'})
	if __addon__.getSetting('search-integration') == 'true':
		if __addon__.getSetting('search-integration-movie-library') == 'true':
			util.add_dir(__language__(30006),{'search-plugin':'plugin://plugin.video.movie-library.cz','url':info['url'],'action':'search'})
		if __addon__.getSetting('search-integration-ulozto') == 'true':
			util.add_dir(__language__(30003),{'search-plugin':'plugin://plugin.video.movie-library.cz','url':info['url'],'action':'search-ulozto'})
		if __addon__.getSetting('search-integration-bezvadata') == 'true':
			util.add_dir(__language__(30004),{'search-plugin':'plugin://plugin.video.bezvadata.cz','url':info['url'],'action':'search'})
		if __addon__.getSetting('search-integration-kinotip') == 'true':
			util.add_dir(__language__(30005),{'search-plugin':'plugin://plugin.video.kinotip.cz','url':info['url'],'action':'search'})
	for m in re.finditer('<option value=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		url  = info['url']+'/videa/-filtr-'+m.group('url')
		xbmc_info['Title'] = '%s - %s' %(info['title'],m.group('name'))
		util.add_video(m.group('name'),{'play':url},info['img'],infoLabels=xbmc_info,menuItems={__language__(30007):'Action(info)'})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def search_plugin(plugin,url,action):
	info = scrapper.get_info(url)
	titles = info['search-title']
	for title in info['search-title']:
	 	add_plugin_call(__language__(30008)+' : '+title,plugin,{action:title})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def add_plugin_call(name,plugin,params,logo='',infoLabels={}):
	name = util.decode_html(name)
	infoLabels['Title'] = name
	liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png',thumbnailImage=logo)
        try:
		liz.setInfo( type='Video', infoLabels=infoLabels )
	except:
		traceback.print_exc()
	plugurl = util._create_plugin_url(params,plugin)
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=plugurl,listitem=liz,isFolder=True)

p = util.params()
use_cache= __addon__.getSetting('cache-meta') == 'true'
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
	root()
if 'kino' in p.keys():
	kino(p)
if 'search-plugin' in p.keys():
	search_plugin(p['search-plugin'],p['url'],p['action'])
if 'item' in p.keys():
	item(p)
if 'play' in p.keys():
	play(p['play'])
