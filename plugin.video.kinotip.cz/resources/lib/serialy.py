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


import xbmc,xbmcplugin,re,sys,urllib2,xbmcgui,random,os
import util,common,md5

SERVER='serialy'
BASE_URL='http://serialy.kinotip.cz/'

def add_dir(name,params,logo='',infoLabels={}):
	params['server']=SERVER
	if not logo == '':
		if logo.find('http') < 0 and not os.path.exists(logo):
			if logo[0] == '/':
				logo = logo[1:]
			logo = BASE_URL+logo
     	return util.add_dir(name,params,logo,infoLabels)

def add_stream(name,url,logo='',infoLabels={}):
	return util.add_video(
		name=name,
		params={'server':SERVER,'play':url},
		logo=logo,
		infoLabels=infoLabels
	)

def _get_meta(name,link):
	# load meta from disk or download it (slow for each serie, thatwhy we cache it)
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	local = os.path.join(local,'serialy-cache')
	if not os.path.exists(local):
		os.makedirs(local)
	m = md5.new()
	m.update(name)
	image = os.path.join(local,m.hexdigest()+'_img.jpg')
	plot = os.path.join(local,m.hexdigest()+'_plot.txt')
	if not os.path.exists(image):
		data = util.request(link)
		_get_image(data,image)
		_get_plot(data,plot)
	return image,_load(plot)

def _save(data,local):
	util.info('Saving file %s' % local)
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

def _get_image(data,local):
 		data = util.substr(data,'<div class=\"entry\"','</div>')
		m = re.search('<img(.+?)src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			img = m.group('img')
			if img.find('http') < 0 :
				if img[0]=='/':
					img = img[1:]
				img = BASE_URL+img
			util.info(' Downloading %s' % img)
			_save(util.request(img),local)

def _get_plot(data,local):
 		data = util.substr(data,'<div class=\"entry\"','</p>')
		m = re.search('<br[^>]+>(?P<plot>(.+?))<', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			_save(util.decode_html(m.group('plot').strip()).encode('utf-8'),local)

def list_series(data):
	pattern='<li[^>]+><a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	add_dir(__language__(30009),{'latest':''})
	for m in re.finditer(pattern, util.substr(data,'<h2>Kategorie seriálů</h2>','</ul>'), re.IGNORECASE | re.DOTALL):
		image,plot = _get_meta(m.group('cat'),m.group('link'))
		add_dir(m.group('cat'),{'cat':m.group('link')},image,{'Plot':plot})


def list_episodes(data):
	pattern = '<div class=\"post\"(.+?)<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(.+?)<img(.+?)src=\"(?P<img>[^\"]+)[^>]+><br[^>]+>(?P<plot>(.+?))<br[^>]+'
	for m in re.finditer(pattern,util.substr(data,'<div class=\"content\"','<div class=\"sidebar\"'),re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'),{'episode':m.group('url')},m.group('img'),infoLabels={'Plot':m.group('plot')})
	data = util.substr(data,'<div id=\'wp_page_numbers\'>','</div>')
	k = re.search('<li class=\"page_info\">(?P<page>(.+?))</li>',data,re.IGNORECASE | re.DOTALL)
	if not k == None:
		n = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>\&lt;</a>',data,re.IGNORECASE | re.DOTALL)
		if not n == None:
			add_dir(k.group('page')+' - jít na předchozí',{'cat':n.group('url')})
		m = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>\&gt;</a>',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			add_dir(k.group('page')+' - jít na další',{'cat':m.group('url')})

def _server_name_full(url):
	return re.search('http\://([^/]+)',url,re.IGNORECASE | re.DOTALL).group(1)
def _server_name(url):
	return re.search('/(.+?)\\.php',url,re.IGNORECASE | re.DOTALL).group(1)+'.com'

def episode(data):
	data = util.substr(data,'<div class=\"content\"','<div class=\"sidebar\"')
	pattern = '<embed src=\"(?P<embed>[^\"]+)(.+?)</p>'
	source = 1
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL):
		add_stream('Zdroj %d - %s' % (source,_server_name_full(m.group('embed'))),m.group('embed'))
		source += 1
	for m in re.finditer('<a href=\"(?P<embed>(/putlocker|/novamov|/videoweed/shockshare)[^\"]+)',data,re.IGNORECASE | re.DOTALL):
		add_stream('Zdroj %d - %s' % (source,_server_name(m.group('embed'))),m.group('embed'))
		source += 1

def handle(params):
	if len(params)==1:
		list_series(util.request(BASE_URL))
	if 'latest' in params.keys():
		list_episodes(util.request(BASE_URL))
	if 'cat' in params.keys():
		list_episodes(util.request(params['cat']))
	if 'episode' in params.keys():
		episode(util.request(params['episode']))
	if 'play' in params.keys():
		common.play(__addon__,'serialy.kinotip.cz',BASE_URL,params['play'])
	return xbmcplugin.endOfDirectory(int(sys.argv[1]))
	