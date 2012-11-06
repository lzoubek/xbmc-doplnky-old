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
import util,resolver, search

from provider import ContentProvider

class PlaymovieContentProvider(ContentProvider):
	

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'play-movie.eu','http://www.play-movie.eu/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories']
		

	def search(self,keyword):
                return self.film(util.request(self._url('index.php?search='+keyword+'&hledat=Hledat')))
		
			
	def film(self,page):
		result=[]
		
		data = util.substr(page,'<div id="font">','<div id="pravy">')
		im = data.find('<img')
		if im > 0:
			pattern='<img src=(?P<img>.+?)></div>.*?class=\'nazev-view\'><a href=\'(?P<url>.+?)\'.?>(?P<name>.+?)</a></div>.*?class=\'popis-view\'>(?P<info>.+?)<'
		else:
			pattern='<a href=\'(?P<url>.+?)\'.?>(?P<name>.+?)</a>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			try:
				item['img'] = m.group('img')
			except:
				pass
			item['url'] = self._url(m.group('url'))
			item['title'] = m.group('name')
			#item['plot']= m.group('info')
			result.append(item)
			
		
		pattern='.+<a href="(?P<url>.+?)">Další</a'
		m = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
		next_url=''
		if not m == None:
			next_url=self._url('index.php'+m.group('url'))
			try:	
				item = self.dir_item()
				item['title'] = 'Další strana ...'
				item['url'] = '#film#'+next_url
				result.append(item)
			except:
				pass
		
		return result

	def cat(self,page):
		result = []
		
		data = util.substr(page,'<menu>','</menu>')
		pattern='a href="(?P<url>.+?)">(?P<name>.+?)</a>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.dir_item()
			item['title']=m.group('name')
			item['url'] = '#film#'+self._url(m.group('url'))
			result.append(item)
		return result
		
	
	def categories(self):
		result = []
		
		search.item()
		
		item = self.dir_item()
		item['type'] = 'new'
		item['url']  = '#last#'+self.base_url
		result.append(item)
		
		item=self.dir_item()
		item['title']='Kategorie filmů'
		item['url']  = '#cat#'+self.base_url
		result.append(item)
		
		return result
	
	
	def list(self,url):
		if url.find('#film#') == 0:
                        return self.film(util.request(self._url(url[6:])))
		if url.find('#cat#') == 0:
                        return self.cat(util.request(self._url(url[5:])))
		if url.find('#last#') == 0:
                        return self.film(util.request(self._url(url[6:])))
		else:
                        raise Expception("Invalid url, I do not know how to list it :"+url)

                        
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		#print 'URL: '+url
		hdata = util.request(url)
		
		data = util.substr(hdata,'<div id=\'video\'>','<div id="pravy">')
			
		resolved = resolver.findstreams(data,['flash[V|v]ars=\"(?P<url>id=.+?)\" ','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]','href="(?P<url>http://(www.)?streamcloud\.eu.+?)"'])
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
	

