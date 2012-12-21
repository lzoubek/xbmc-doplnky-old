# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Ivo Brhel
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

import re,os,urllib,urllib2,cookielib
import util,resolver
import simplejson as json

from provider import ContentProvider

class PetkaContentProvider(ContentProvider):
	

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'petka.cz','http://www.petka.cz/porady/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories']
		
		
	def next_film(self,url):
		result = []

		data = url.split('#')
		nurl = data[0]
		pg   = int(data[1])
		
		url = '%s?strana=%d' % (nurl,pg)
		page = util.request(url,{'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'})
		
		data = json.loads(page)
		state = data['state']
		nextpg= data['next_page']
		
		pattern = '<a.+?href="(?P<url>[^"]+)".*?><img src="(?P<img>.[^"]+)".*?alt="(?P<name>[^"]+)".*?/></a>' 
		for m in re.finditer(pattern,data['data'].encode('utf-8'),re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['url']   = m.group('url')
			item['title'] = m.group('name')
			item['img']   = m.group('img')
			result.append(item)
			
		if nextpg:
			next_page = 'Další >>'
			#next_url  = '%s?strana=%d' % (nurl,pg+1)
			next_url  = '%s#%d' % (nurl,pg+1) 
			   
			try:	
				item = self.dir_item()
				item['type'] = 'next'
				item['title'] = next_page
				item['url'] = '#nfilm#'+next_url
				result.append(item)
			except:
				pass
			
			
		
		return result
		
	def film(self,page):
		result=[]
		data = util.substr(page,'<div id="episodesAll" class="episodes tabContent">','<div id="episodesTop"')
		pattern = '<a.+?href="(?P<url>[^"]+)".*?><img src="(?P<img>.[^"]+)".*?alt="(?P<name>[^"]+)".*?/></a>' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['url']   = m.group('url')
			item['title'] = m.group('name')
			item['img']   = m.group('img')
			result.append(item)
		
		pattern = 'data-ajax_href="(?P<url>[^"]+)".+?data-ajax_page="(?P<page>[^"]+)"' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			
			if m.group('page') != '':
				#print '--dalsi strana'
				next_page = 'Další >>'
				#next_url  = '%s?strana=%d' % (m.group('url'),int(m.group('page'))+1)
				next_url  = '%s#%d' % (m.group('url'),int(m.group('page'))+1) 
				
		try:	
			
			item = self.dir_item()
			item['type'] = 'next'
			item['title'] = next_page
			item['url'] = '#nfilm#'+next_url
			result.append(item)
			
		except:
			pass
		
		return result
		
	
	def categories(self):
		#result = []
                result = self.episodes(util.request(self.base_url))
		
		return result
		
		
	def episodes(self,page):
		result = []
		od='<h2 class="cufon">Všechny pořady abecedně</h2>'
		do='<div class="container100 wideLine"></div>'
		data = util.substr(page,od,do)
		pattern = '<img src=\"(?P<img>[^\"]+)\"[\s|\S]*?<a.+?href="(?P<url>.+?)">(?P<name>.+?)</a>[\s|\S]*?<p>(?P<info>.+?)</p>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.dir_item()
			item['title'] = m.group('name')
			item['url'] = '#film#'+m.group('url')
			item['img'] = m.group('img')
			item['plot']= m.group('info')
			result.append(item)
		return result
	
		
		
	def list(self,url):
		if url.find('#nfilm#') == 0:
                        return self.next_film(url[7:])
		if url.find('#film#') == 0:
                        return self.film(util.request(url[6:]))
		#if url.find('#abc#') == 0:
		#	self.od='<h2 class="cufon">Všechny pořady abecedně</h2>'
		#	self.do='<div class="container100 wideLine"></div>'
                #        return self.episodes(util.request(url[5:]))
		else:
                        raise Expception("Invalid url, I do not know how to list it :"+url)

                        
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		#print 'URL: '+url
		hdata = util.request(url)
		
		data = util.substr(hdata,'<div id="bigPlayer">','</div>')
		
		resolved = resolver.findstreams(data,['flash[V|v]ars=\"(?P<url>id=.+?)\" ','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]','(?P<url>\"http://www.youtube.com/[^\"]+)'])
                result = []
		for i in resolved:
                        item = self.video_item()
                        item['title'] = i['name']
                        item['url'] = i['url'] 
                        item['quality'] = i['quality']
                        item['surl'] = i['surl']
                        result.append(item)  
                if len(result)==1:
                        return result[0]
                elif len(result) > 1 and select_cb:
                        return select_cb(result)
	

