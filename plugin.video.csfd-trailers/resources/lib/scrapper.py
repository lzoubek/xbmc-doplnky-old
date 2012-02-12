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

import xbmc,xbmcplugin,re,sys
import util
import unicodedata

def get_info(url):
	info = _empty_info()
	cached = __cache__.get(url)
	if '' == cached:
		util.info('Not in cache : '+url)
		page = util.request(url)
		info['title'] = _get_title(page)
		info['search-title'] = _search_title(page)
		info['url'] = url
		info['img'] = _get_img(page)
		info['plot'] = _plot(page)
		country,info['year'] = _origin(page)
		info['percent'],info['rating'] = _rating(page)
		__cache__.set(url,repr(info))
		return info
	else:
		return eval(cached)

def xbmc_info(info):
	ret  = {}
	ret['Plot'] = info['plot']
	ret['Year'] = info['year']
	ret['Genre'] = info['genre']
	ret['Rating'] = info['rating']
	return ret

def _get_img(page):
	data  = util.substr(page,'<div id=\"poster\"','</div>')
	return re.search('src=\"([^\"]+)',data).group(1)

def _get_title(page):
	data  = util.substr(page,'<meta property=\"og:title\"','>')
	return re.search('content=\"([^\"]+)',data).group(1)

def _search_title(page):
	titles = []
	data  = util.substr(page,'<div class=\"info','</div>')
	p = re.search('<[hH]1>([^<]+)',data).group(1)
	p = re.sub('[\t\r\n]+',' ',p).strip()
	p = unicode(p,'utf-8',errors='ignore')	
	titles.append(util.replace_diacritic(p))
	for m in re.finditer('<li>.+?<h3>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		p = re.sub('[\t\r\n]+',' ',m.group('name')).strip()
		p = unicode(p,'utf-8',errors='ignore')
		titles.append(util.replace_diacritic(p))
	return titles
def _origin(page):
	origin = re.search('<p class=\"origin\">([^<]+)',page).group(1)
	data = origin.split(',')
	if len(data) > 1:
		try:
			return data[0].strip(),int(data[1].strip())
		except:	
			return data[0].strip(),0
	return '',''
def _plot(page):
	data = util.substr(page,'<div id=\"plots\"','</ul>')
	m = re.search('<ul>([^$]+)',data)
	if m:
		p = re.sub('</li>','[CR]',m.group(1))
		p = re.sub('<(div|span|li)[^>]*>','',p)
		p = re.sub('</div>|</span>','',p)
		p = re.sub('<a[^>]*>','[B]',p)
		p = re.sub('</a>','[/B]',p)
		p = re.sub('<em>','[I]',p)
		p = re.sub('</em>','[/I]',p)
		p = re.sub('<img[^>]+>','',p)
		p = re.sub('[\ \t\r\n]+',' ',p)
		p = util.decode_html(p)
		return p
	return ''

def _rating(page):
	data = util.substr(page,'<div id=\"rating\"','</div>')
	m = re.search('<[hH]2[^>]+>(\d+)',data)
	if m:
		return m.group(1)+'%', float(m.group(1))/10
	return '',0

def _empty_info():
	return {
			'title':'',
			'search-title':[],
			'url':'',
			'plot':'',
			'img':'',
			#'streams': [{'url':'','name':''}],
			'streams': [],
			'genre':'',
			'year': 0,
			'rating':0,
			'percent':'0%',
			'votes':0,
			'director':''
		}


