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

import xbmc,xbmcplugin,re,sys,urllib2,xbmcgui,random
import util,common
SERVER='divx'
BASE_URL='http://divx.kinotip.cz/'

def add_dir(name,params,logo='',infoLabels={}):
	params['server']=SERVER
	if not logo == '':
		if logo.find('/') == 0:
			logo = logo[1:]
		if logo.find('http://') < 0:
			logo = BASE_URL+logo
     	return util.add_dir(name,params,logo,infoLabels)

def add_stream(name,url,logo='',infoLabels={}):
	return util.add_video(
		name=name,
		params={'server':SERVER,'play':url},
		logo=logo,
		infoLabels=infoLabels
	)

def root():
	add_dir('Kategorie filmů',{'list':'categories'})
	add_dir('Filmy podle herců',{'list':'artists'})
	add_dir('Filmy podle roku',{'list':'years'})
	add_dir('Vyhledat',{'search':'string'})



def listing(param):
	data = util.request(BASE_URL)
	if 'categories' == param:
		return listing_categories(data)
	if 'artists' == param:
		return listing_artists(data)
	if 'years' == param:
		return listing_years(data)

def listing_categories(data):
	pattern='<li[^>]+><a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, util.substr(data,'<h2>Kategorie DIVX filmů</h2>','</ul>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),{'cat':m.group('link')})

def listing_artists(data):
	pattern='<a href=\'(?P<link>[^\']+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, util.substr(data,'<h2>Filmy podle herců</h2>','</li>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),{'cat':m.group('link')})

def listing_years(data):
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, util.substr(data,'<h2>Filmy podle roku</h2>','</ul>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),{'cat':m.group('link')})
def search():
	kb = xbmc.Keyboard('','Vyhledat',False)
	kb.doModal()
	if kb.isConfirmed():
		data = util.request(BASE_URL+'?s='+kb.getText())
		return list_movies(data)

def list_movies(data):
	pattern = '<div class=\"post\"(.+?)<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(.+?)<img(.+?)src=\"(?P<img>[^\"]+)[^>]+><br[^>]+>(?P<plot>(.+?))<br[^>]+'
	for m in re.finditer(pattern,util.substr(data,'<div class=\"content\"','<div class=\"sidebar\"'),re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'),{'movie':m.group('url')},m.group('img'),infoLabels={'Plot':m.group('plot')})
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

def movie(data):
	data = util.substr(data,'<div class=\"content\"','<div class=\"sidebar\"')
	pattern = '<iframe(.+?)src=[\"\'](?P<embed>http\://stagevu(.+?))[\"\'](.+?)'
	source = 1
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL):
		add_stream('Zdroj %d - %s' % (source,_server_name_full(m.group('embed'))),m.group('embed'))
		source += 1
	for m in re.finditer('<a href=\"(?P<embed>(/putlocker|/novamov|/videoweed|/movshare|/divxstage)[^\"]+)',data,re.IGNORECASE | re.DOTALL):
		add_stream('Zdroj %d - %s' % (source,_server_name(m.group('embed'))),m.group('embed'))
		source += 1

	
def handle(params):
	if len(params)==1:
		root()
	if 'list' in params.keys():
		listing(params['list'])
	if 'search' in params.keys():
		search()
	if 'cat' in params.keys():
		list_movies(util.request(params['cat']))
	if 'movie' in params.keys():
		movie(util.request(params['movie']))
	if 'play' in params.keys():
		common.play('divx.kinotip.cz',BASE_URL,params['play'])
	return xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
