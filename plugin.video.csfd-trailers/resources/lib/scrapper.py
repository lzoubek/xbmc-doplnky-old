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

import xbmc,xbmcplugin,re,sys,traceback
import util
import xbmcutil
import unicodedata

def get_info(url):
	cached = get_cached_info(url)
	if cached:
		return cached
	else:
		info = _empty_info()
		util.info('Not in cache : '+url)
		try:
			page = util.request(url,headers={'Referer':BASE_URL,'User-Agent':util.UA})
		except:
			util.error('Unable to read page '+url)
			traceback.print_exc()
			info['url'] = url
			return info
		info['title'] = _get_title(page)
		info['search-title'] = _search_title(page)
		info['url'] = url
		info['trailers_url'] = url.rstrip('/')+'/videa/'
		info['cast'] = _cast(page)
		info['genre'] = _genre(page)
		info['img'] = _get_img(page)
		info['plot'] = _plot(page)
		country,info['year'] = _origin(page)
		info['percent'],info['rating'] = _rating(page)
		info['director'] = _director(page)
		info['votes'] = _votes(page)
		_validate(info)
		set_info(info)
		return info

def get_cached_info(url):
	info = __cache__.get(url)
	if not '' == info:
		ret = eval(info)
		_validate(ret)
		return ret

def set_info(info):
	__cache__.set(info['url'],repr(info))

def xbmc_info(info):
	ret  = {}
	ret['Plot'] = info['plot']
	ret['Plotoutline'] = info['plot'][:100]+'...'
	ret['Year'] = info['year']
	ret['Genre'] = info['genre']
	ret['Rating'] = info['rating']
	ret['Director'] = info['director']
	ret['Votes'] = info['votes']
	ret['Cast'] = info['cast']
	ret['Trailer'] = info['trailer']
	ret['Title'] = info['title']
	return ret

def _validate(info):
	dummy = _empty_info()
	for key in info.keys():
		if not type(info[key]) == type(dummy[key]):
			util.info('key '+key+' is type of '+str(type(info[key]))+' does not match required type '+str(type(dummy[key])))
			info[key] = dummy[key]
	for key in dummy.keys():
		if not key in info:
			info[key] = dummy[key]

def _match(m,default=None):
	if m:
		return m.group(1)
	return default

def _votes(page):
	num = _match(re.search('<a id=\"rating-count-link[^>]+>.+?\(([^\)]+)',page))
	try:
		num = ''.join(re.findall('\d',num))
		return str(int(num))
	except:
		return __empty_info['votes']

def _cast(page):
	data  = util.substr(page,'<h4>Hrají:','</span>')
	return re.findall('<a[^>]+>([^<]+)',data,re.IGNORECASE)

def _genre(page):
	return _match(re.search('<p class=\"genre\">([^<]+)',page),__empty_info['genre'])

def _get_img(page):
	data =  util.substr(page,'<div id=\"profile\"','</div>')
	return _match(re.search('src=\"([^\"]+)',data),__empty_info['img'])

def _get_title(page):
	data  = util.substr(page,'<meta property=\"og:title\"','>')
	return _match(re.search('content=\"([^\"]+)',data))

def _director(page):
	data  = util.substr(page,'<h4>Režie:','</span>')
	return _match(re.search('<a[^>]+>([^<]+)',data),__empty_info['director'])

def _search_title(page):
	titles = []
	data  = util.substr(page,'<div class=\"info','</div>')
	p = _match(re.search('<[hH]1>([^<]+)',data))
	if not p:
		return __empty_info['title']
	p = re.sub('[\t\r\n]+',' ',p).strip()
	p = unicode(p,'utf-8',errors='ignore')	
	titles.append(util.replace_diacritic(p))
	for m in re.finditer('<li>.+?<h3>(?P<name>[^<]+)',data,re.DOTALL|re.IGNORECASE):
		p = re.sub('[\t\r\n]+',' ',m.group('name')).strip()
		p = unicode(p,'utf-8',errors='ignore')
		titles.append(util.replace_diacritic(p))
	return titles

def _origin(page):
	origin = _match(re.search('<p class=\"origin\">([^<]+)',page))
	if not origin:
		return '',__empty_info['year']
	data = origin.split(',')
	if len(data) > 1:
		try:
			return data[0].strip(),int(data[1].strip())
		except:	
			return data[0].strip(),0
	return '',__empty_info['year']
def _plot(page):
	data = util.substr(page,'<div id=\"plots\"','</ul>')
	m = _match(re.search('<ul>([^$]+)',data))
	if m:
		p = re.sub('</li>','[CR]',m)
		p = re.sub('<br[^>]*>','[CR]',p)
		p = re.sub('<(li|div|span)[^>]*>','',p)
		p = re.sub('</div>|</span>','',p)
		p = re.sub('<a[^>]*>','[B]',p)
		p = re.sub('</a>','[/B]',p)
		p = re.sub('<em>','[I]',p)
		p = re.sub('</em>','[/I]',p)
		p = re.sub('<strong>','[B]',p)
		p = re.sub('</strong>','[/B]',p)
		p = re.sub('<img[^>]+>','',p)
		p = re.sub('[\ \t\r\n]+',' ',p)
		p = util.decode_html(p)
		return p
	return __empty_info['plot']

def _rating(page):
	data = util.substr(page,'<div id=\"rating\"','</div>')
	m = _match(re.search('<[hH]2[^>]+>(\d+)',data))
	if m:
		return m+'%', float(m)/10
	return __empty_info['percent'],__empty_info['rating']

def _empty_info():
	return __empty_info.copy()

__empty_info = {
			'title':'',
			'search-title':[],
			'url':'',
			'trailers_url':'',
			'plot':u'',
			'img':'',
			'trailer': '',
			'cast':[],
			'genre':'',
			'year': 0,
			'rating':0.0,
			'percent':'0%',
			'votes':'0',
			'director':''
		}


