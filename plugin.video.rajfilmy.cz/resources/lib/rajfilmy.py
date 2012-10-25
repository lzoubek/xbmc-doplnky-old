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

from provider import ContentProvider

class RajfilmyContentProvider(ContentProvider):
	
	od=''
	do=''
	serial=False

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'rajfilmy.cz','http://www.rajfilmy.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories']
		
	def getInfo(self,link):
		data = util.request(link)
		data = util.substr(data,'<p id=\"file_rating\">','<div class=\"clear\">')
		pattern = 'id=\"file_rating\">(?P<rating>.+?)</p>[\s|\S]*?<p>(?P<info>.+?)</p>[\s|\S]*?<p class=\"file_info\">Přidáno: (?P<date>.+?)</p>'
		m = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			return m.group('rating'),m.group('info'),m.group('date')
		else:
			return '','',''
		
	def film(self,page):
		result=[]
		if self.serial:
			data = util.substr(page,'<div class=\"content_box\">','<div class=\"clear\"></div>')
		else:
			data = util.substr(page,'<div class=\"kategorie_box\">','<div id=\"menu_prave\">')
		pattern = '<img src=\"(?P<img>[^\"]+)\"[\s|\S]*?<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			if self.serial: 
				item = self.dir_item()
				item['url'] = '#film#'+m.group('url')
			else:
				item = self.video_item()
				item['url'] = m.group('url')
				
			item['title'] = m.group('name')
			item['img'] = m.group('img')
			result.append(item)
			
		data = util.substr(page,'<div class=\"pagination\">','</div>')
		pattern = '<a[\s|\S]*?href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			
			if m.group('name') == '&rsaquo;':
				#print '--dalsi strana'
				next_page = m.group('url')[41:].replace('.html','')
				next_url  = m.group('url')
			if m.group('name') == '&lrsaquo':
				#print '--predchozi strana'
				prev_url = m.group('url')
			if m.group('name')== '&rsaquo;&rsaquo;':
				#print '--posledni strana'
				last_page = m.group('url')[41:].replace('.html','')
			
		try:	
			
			item = self.dir_item()
			item['title'] = 'Přejít na stranu '+ next_page+' z '+ str(last_page)
			item['url'] = '#film#'+next_url
			result.append(item)
			
		except:
			pass
		
		return result

	
	def categories(self):
		result = []

		item = self.dir_item()
		item['type'] = 'top'
		item['url']  = '#pop#'+self.base_url
		result.append(item)
		
		item = self.dir_item()
		item['type'] = 'new'
		item['url']  = '#last#'+self.base_url
		result.append(item)
		
		item=self.dir_item()
		item['title']='Filmy'
		item['url']  = '#film#'+self._url('kategorie/7/Filmy/1.html')
		result.append(item)
		
		item=self.dir_item()
		item['title']='Serialy'
		item['url']  = '#serial#'+self._url('kategorie/17/Seriály/1.html')
		result.append(item)
		
		return result
		
	def episodes(self,page):
		result = []
		data = util.substr(page,self.od,self.do)
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['title'] = m.group('name')
			item['url'] = m.group('url')
			result.append(item)
		return result
	
	def list(self,url):
		if url.find('#film#') == 0:
			self.serial=False
                        return self.film(util.request(self._url(url[6:])))
		if url.find('#serial#') == 0:
			self.serial=True
                        return self.film(util.request(self._url(url[8:])))
		if url.find('#pop#') == 0:
			self.od='<div class=\"content_box_nejpopul\">'
			self.do='</div>'
                        return self.episodes(util.request(self._url(url[:5])))
		if url.find('#last#') == 0:
			self.od='<div class=\"content_box_nejnovejsi\"><ol>'
			self.do='</div>'
                        return self.episodes(util.request(self._url(url[:6])))
		else:
                        raise Expception("Invalid url, I do not know how to list it :"+url)

                        
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		#print 'URL: '+url
		hdata = util.request(url)
		
		data = util.substr(hdata,'<div id=\"file_box"','<ul class="tab_menu"')
		
		resolved = resolver.findstreams(data,['flash[V|v]ars=\"(?P<url>id=.+?)\" ','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]','(?P<url>\"http://www.youtube.com/[^\"]+)'])
                result = []
		for i in resolved:
			print i
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
	

