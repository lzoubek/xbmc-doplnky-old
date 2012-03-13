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

import re,os,urllib,urllib2,traceback,time
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
__scriptid__   = 'plugin.video.csfd-trailers'
__scriptname__ = 'ČSFD Trailery'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )

try:
	import StorageServer
except:
	import storageserverdummiest as StorageServer

__cache__ = StorageServer.StorageServer(__scriptid__, 1*24*30)

import scrapper

BASE_URL='http://www.csfd.cz/'
scrapper.__cache__ = __cache__
scrapper.BASE_URL = BASE_URL
import util,resolver,search

def _search_movie_cb(what):
	print 'searching for movie '+what
	url = BASE_URL+'hledat/complete-films/?q='+urllib.quote(what)
	page = util.request(url)

	results = []
	data = util.substr(page,'<div id=\"search-films','<div class=\"footer')
	for m in re.finditer('<h3 class=\"subject\"[^<]+<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+).+?<p>(?P<info>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		results.append((m.group('url'),'%s (%s)' %(m.group('name'),m.group('info'))))
	
	for m in re.finditer('<li(?P<item>.+?)</li>',util.substr(data,'<ul class=\"films others','</div'),re.DOTALL|re.IGNORECASE):
		base = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',m.group('item'))
		if base:
			name = base.group('name')
			for n in re.finditer('<span[^>]*>(?P<data>[^<]+)',m.group('item')):
				name = '%s %s' % (name,n.group('data'))
			results.append((base.group('url'),name))
	if preload():
		return preload_items(results)
	add_items(results)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def _search_person_cb(what):
	print 'searching for '+what
	page = util.request(BASE_URL+'hledat/complete-films/?q='+urllib.quote(what))

	results = []
	data = util.substr(page,'<div id=\"search-creators','<div class=\"footer')
	for m in re.finditer('<h3 class=\"subject\"[^<]+<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+).+?<p>(?P<info>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		results.append((m.group('url'),m.group('name')+' ('+m.group('info')+')'))
	
	for m in re.finditer('<li(?P<item>.+?)</li>',util.substr(data,'<ul class=\"creators others','</div'),re.DOTALL|re.IGNORECASE):
		base = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',m.group('item'))
		if base:
			name = base.group('name')
			for n in re.finditer('<span[^>]*>(?P<data>[^<]+)',m.group('item')):
				name = '%s %s' % (name,n.group('data'))
			results.append((base.group('url'),name))
	for url,name in results:
		info = scrapper._empty_info()
		info['url'] = url
		add_person(name,info)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
	search.item({'s':'movie'},label=util.__lang__(30003)+' '+__language__(30017))
	search.item({'s':'person'},label=util.__lang__(30003)+' '+__language__(30018))
	util.add_dir('Kino',{'kino':''},icon())
	util.add_dir('Žebříčky',{'top':''},util.icon('top.png'))
	util.add_dir('Blu-ray',{'dvd':'bluray'},icon())
	util.add_dir('Premiérová DVD',{'dvd':'dvd_retail'},icon())
	util.add_dir('Levná DVD v trafikách a časopisech',{'dvd':'dvd_lite'},icon())
	util.add_dir('Tvůrci',{'artists':''},icon())
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def add_person(name,info):
	xbmc_info = scrapper.xbmc_info(info)
	util.add_dir(name,{'person':furl(info['url'])},'DefaultArtist.png',infoLabels=xbmc_info)

def add_item(name,info):
	xbmc_info = scrapper.xbmc_info(info)
	if not '0%' == info['percent']:
		name += ' '+info['percent']
	util.add_dir(name,{'item':furl(info['url'])},info['img'],infoLabels=xbmc_info,
		menuItems={
			__language__(30007):'Action(info)',
			__language__(30001):{'preload-refresh':''},
		})

def add_items(items):
	for url,name in items:
		info = scrapper.get_cached_info(furl(url))
		if info:
			add_item(name,info)
		else:
			info = scrapper._empty_info()
			info['url'] = url
			add_item(name,info)

def preload_items(results):
	step = 100./len(results)
	prog = 0
	pDialog = xbmcgui.DialogProgress()
	progress = pDialog.create(__language__(30019))
	pDialog.update(prog,__language__(30019))
	for url,name in results:
		if pDialog.iscanceled():
			pDialog.close()
			return
		prog = float(prog + step)
		pDialog.update(int(prog),__language__(30019),name)
		if not scrapper.get_cached_info(furl(url)):
			scrapper.get_info(furl(url))
			time.sleep(3)
	pDialog.close()

def kino(params):
	if 'kino-year' in params.keys() and 'kino-country' in params.keys():
		return kino_list('kino/prehled/?country=%s&year=%s' % (params['kino-country'],params['kino-year']))
	if 'kino-country' in params.keys():
		data = util.request(furl('kino/prehled'))
		data = util.substr(data,'id=\"frmfilter-year','</select>')
		for m in re.finditer('<option value=\"(?P<value>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			params['kino-year'] = m.group('value')
			util.add_dir(
				m.group('name'),
				params,
			)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
	else:
		data = util.request(furl('kino/prehled'))
		data = util.substr(data,'id=\"frmfilter-country','</select>')
		for m in re.finditer('<option value=\"(?P<value>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			params['kino-country'] = m.group('value')
			util.add_dir(m.group('name'),params)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def kino_list(url):
	page = util.request(furl(url))
	data = util.substr(page,'<div id=\"releases\"','<div class=\"footer\">')
	results = []
	for m in re.finditer('<td class=\"date\">(?P<date>[^<]*).+?<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+).+?<span class=\"film-year\">(?P<year>[^<]+)',data,re.IGNORECASE|re.DOTALL):
		name = '%s %s %s' % (m.group('date'),m.group('name'),m.group('year'))
		results.append((m.group('url'),name))
	if preload():
		preload_items(results)
	else:
		add_items(results)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_addon_search(label,addon,info,action):
	util.add_dir(__language__(label),{'search-plugin':'plugin://%s' % addon,'url':info['url'],'action':action},xbmcaddon.Addon(addon).getAddonInfo('icon'))

def item(params):
	info = scrapper.get_info(params['item'])
	xbmc_info = scrapper.xbmc_info(info)
	page = util.request(info['trailers_url'],headers={'Referer':BASE_URL})
	data = util.substr(page,'<label for=\"frmfilterSelectForm-filter\">','</select>')
	util.add_dir(__language__(30007),params,info['img'],infoLabels=xbmc_info,menuItems={__language__(30007):'Action(info)'})
	if __addon__.getSetting('search-integration') == 'true':
		if __addon__.getSetting('search-integration-movie-library') == 'true':
			add_addon_search(30006,'plugin.video.movie-library.cz',info,'search')
		if __addon__.getSetting('search-integration-ulozto') == 'true':
			add_addon_search(30003,'plugin.video.movie-library.cz',info,'search-ulozto')
		if __addon__.getSetting('search-integration-bezvadata') == 'true':
			add_addon_search(30004,'plugin.video.bezvadata.cz',info,'search')
		if __addon__.getSetting('search-integration-kinotip') == 'true':
			add_addon_search(30005,'plugin.video.kinotip.cz',info,'search')
	def_trailer = None
	for m in re.finditer('<option value=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		url  = info['url']+'/videa/-filtr-'+m.group('url')
		trailer = util._create_plugin_url({'play':url})
		if def_trailer == None:
			info['trailer'] = trailer
			scrapper.set_info(info)
		xbmc_info['Title'] = '%s - %s' %(info['title'],m.group('name'))
		util.add_video(m.group('name'),{'play':url},info['img'],infoLabels=xbmc_info,menuItems={__language__(30007):'Action(info)'})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def person(params):
	info = scrapper.get_info(params['person'])
	xbmc_info = scrapper.xbmc_info(info)
	page = util.request(info['url'],headers={'Referer':BASE_URL})
	data = util.substr(page,'<div id=\"filmography\"','<div id=\"fanclub\"')
	results = []
	for m in re.finditer('<td(?P<item>.+?)</td>',data,re.DOTALL|re.IGNORECASE):
		base = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',m.group('item'))
		if base:
			name = base.group('name')
			for n in re.finditer('<span[^>]*>(?P<data>[^<]+)',m.group('item')):
				name = '%s %s' % (name,n.group('data'))
			results.append((base.group('url'),name))
	if preload():
		return preload_items(results)
	add_items(results)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def search_plugin(plugin,url,action):
	info = scrapper.get_info(url)
	titles = info['search-title']
	params = {}
	if __addon__.getSetting('search-integration-update-history') == 'false':
		params['search-no-history'] = ''
	for title in info['search-title']:
		params[action] = title
	 	add_plugin_call(__language__(30008)+': '+title,plugin,params,util.icon('search.png'))
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

def top(params):
	if 'top-select' in params.keys():
		url = furl(params['top-select']+'?show=complete')
		page = util.request(url)
		data = util.substr(page,'<table class=\"content','</table>')
		results = []
		for m in re.finditer('<tr>(?P<data>.+?)</tr>',data,re.DOTALL|re.IGNORECASE):
			item = m.group('data')
			base = re.search('<td class=\"order\">(?P<order>[^<]+).+?<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>',item,re.DOTALL|re.IGNORECASE)
			if base:
				name = '%s %s' % (base.group('order'),base.group('name'))
				for n in re.finditer('<span[^>]*>(?P<data>[^<]+)',item):
					name = '%s %s' % (name,n.group('data'))
				results.append((base.group('url'),name))
		if preload():
			preload_items(results)
		else:
			add_items(results)
			xbmcplugin.endOfDirectory(int(sys.argv[1]))
	else:
		page = util.request(furl('zebricky/'))
		data = util.substr(page,'<div class=\"navigation','</div>')
			
		util.add_dir(
			'Nejlepší filmy',
			{'top':'','top-select':'zebricky/nejlepsi-filmy/'},
			icon(),
			menuItems={__language__(30001):{'preload':'','top':'','top-select':'zebricky/nejlepsi-filmy/'}},
		)
		for m in re.finditer('<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			util.add_dir(
				m.group('name'),
				{'top':'','top-select':m.group('url')},
				icon(),
			)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def dvd(params):
	if 'year' in params.keys():
		return kino_list('dvd-a-bluray/rocne/?format='+params['dvd']+'&year='+params['year'])
	else:
		page = util.request(furl('dvd-a-bluray/rocne/?format='+params['dvd']))
		data = util.substr(page,'id=\"frmfilter-year','</select>')
		for m in re.finditer('<option value=\"(?P<value>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			params['year'] = m.group('value')
			util.add_dir(m.group('name'),params)
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
def artists(params):
	if not 'type' in params.keys():
		page = util.request(furl('tvurci/statistiky'))
		for m in re.finditer('<div id=\"(?P<type>[^\"]+)[^<]+<h2 class=\"header\">(?P<name>[^<]+)',page,re.DOTALL|re.IGNORECASE):
			util.add_dir(m.group('name'),{'artists':'','type':m.group('type')},icon())
		return xbmcplugin.endOfDirectory(int(sys.argv[1]))
	typ = params['type']
	page = util.request(furl('tvurci/statistiky/?expand='+typ))
	data = util.substr(page,'<div id=\"'+typ+'\"','<div class=\"footer')
	results = []
	if not 'subtype' in params.keys():
		for m in re.finditer('<h3 class=\"label\">(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			results.append(m.group('name'))
		if len(results) > 0:
			index = 0
			for name in results:
				params['subtype'] = str(index)
				index+=1
				util.add_dir(name,params,icon())
			return xbmcplugin.endOfDirectory(int(sys.argv[1]))
		else:
			for m in re.finditer('<li[^<]+<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(?P<data>[^<]+)',data,re.DOTALL|re.IGNORECASE):
				results.append((m.group('name')+m.group('data'),m.group('url')))
	else:
		subtype = int(params['subtype'])
		index = 0
		for m in re.finditer('<h3 class=\"label\">(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			if index == subtype:
				subtype = m.group('name')
				break
			index+=1
		data = util.substr(data,subtype,'</div>')
		for m in re.finditer('<li[^<]+<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(?P<data>[^<]+)',data,re.DOTALL|re.IGNORECASE):
			results.append((m.group('name')+m.group('data'),m.group('url')))
	for index,(name,url) in enumerate(results):
		info = scrapper._empty_info()
		info['url'] = url
		add_person('%i. %s' % (index+1,name),info)
	return xbmcplugin.endOfDirectory(int(sys.argv[1]))

def icon():
	return os.path.join(__addon__.getAddonInfo('path'),'icon.png')

def preload():
	return __addon__.getSetting('preload') == 'true'

def preload_refresh():
	p = util.params(__addon__.getSetting('last-url'))
	__addon__.setSetting('preload','true')
	try:
		try:
			main(p)
		except Error, e:
			raise e
	finally:
		__addon__.setSetting('preload','false')
		xbmc.executebuiltin('Container.Refresh')

def main(p):
	if p=={}:
		xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
		root()
	if 'kino' in p.keys():
		kino(p)
	if 'top' in p.keys():
		top(p)
	if 'dvd' in p.keys():
		dvd(p)
	if 'artists' in p.keys():
		artists(p)
	if 'search-plugin' in p.keys():
		search_plugin(p['search-plugin'],p['url'],p['action'])
	if 'item' in p.keys():
		item(p)
	if 'person' in p.keys():
		person(p)
	if 'preload-refresh' in p.keys():
		return preload_refresh()
	if 'play' in p.keys():
		play(p['play'])
	search.main(__addon__,'search_history_movies',p,_search_movie_cb,'s','movie')
	search.main(__addon__,'search_history_persons',p,_search_person_cb,'s','person')

p = util.params()
util.init_urllib()
if __addon__.getSetting('clear-cache') == 'true':
	util.info('Cleaning all cache entries...')
	__addon__.setSetting('clear-cache','false')
	__cache__.delete('http%')
main(p)
__addon__.setSetting('last-url',sys.argv[2])
