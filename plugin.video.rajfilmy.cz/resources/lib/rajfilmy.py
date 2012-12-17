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

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'rajfilmy.cz','http://www.rajfilmy.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories','search']
		
	def search(self,keyword):
		data = util.post(self._url('search.php'),{'t':keyword,'submit':'Hledat'})
                return self.film(data)
		
		
	def film(self,page):
		result=[]
		data = util.substr(page,'<div id="main_contents">','<div class="category_outer">')
		pattern = '<img src=\"(?P<img>[^\"]+)\"[\s|\S]*?<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)[\s|\S]*?<p class=\"popis\">(?P<info>.+?)</p>[\s|\S]*?<div class=\"rok2\">(?P<year>.*?)</div>[\s|\S]*?<div class=\"zanr2\">(?P<genre>.+?)</div>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['url']   = m.group('url')
			item['title'] = m.group('name')
			item['img']   = m.group('img')
			'''
			item['plot']  = m.group('info')
			try:
				item['year']  = int(m.group('year'))
			except:
				pass
			item['genre'] = m.group('genre')
			'''
			result.append(item)
		
		pg='long'
		if page.find('<div class="arrow_nav">')>0:
			data = util.substr(page,'<div class="arrow_nav">','</div>')
			pg='small'
		else:
			data = util.substr(page,'<div class=\"pagination\">','</div>')
		pattern = '<a[\s|\S]*?href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			
			if m.group('name') == '&rsaquo;':
				#print '--dalsi strana'
				next_page = m.group('url')[41:].replace('.html','')
				next_page = next_page.replace('/','')
				next_url  = m.group('url')
			if m.group('name') == '&lrsaquo':
				#print '--predchozi strana'
				prev_url = m.group('url')
			if m.group('name')== '&rsaquo;&rsaquo;':
				#print '--posledni strana'
				last_page = m.group('url')[41:].replace('.html','')
				last_page = last_page.replace('/','')
			if m.group('name') == 'Další &gt;':
				next_page = 'Další >>'
				next_url  = m.group('url').replace('&amp;','&')
		try:	
			
			item = self.dir_item()
			if pg=='long':
				item['title'] = 'Přejít na stranu '+ next_page+' z '+ str(last_page)
			else:
				item['title'] = next_page
			item['url'] = '#film#'+next_url
			result.append(item)
			
		except:
			pass
		
		return result
		
	def cat_det(self,page):
		result = []

		data = util.substr(page,'<ul class="nav_menu">','</div>')
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.dir_item()
			item['title'] = m.group('name')
			item['url'] = '#film#'+m.group('url')
			result.append(item)
		
		return result
	
	def categories(self):
		result = []

		item = self.dir_item()
		item['type'] = 'top'
		item['url']  = '#top#'+self.base_url
		result.append(item)
		
		item = self.dir_item()
		item['type'] = 'new'
		item['url']  = '#new#'+self.base_url
		result.append(item)

		item=self.dir_item()
		item['title']='Kategorie filmu'
		item['url']  = '#cat#'+self.base_url
		result.append(item)

		data = util.substr(util.request(self.base_url),'<div class="kategorie">Kategorie</div>','<!-- BLUEBOARD SHOUTBOARD -->')
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			if m.group('url').find('rnotéka')>0:
				continue
			item = self.dir_item()
			item['title'] = m.group('name')
			if (m.group('url').find('Filmy')>0) or (m.group('url').find('Děti')>0):
				item['url'] = '#film#'+self._url(m.group('url'))
			else:
				#item['url'] = '#serial#'+m.group('url')
				continue
			#item['url'] = '#none#'+m.group('url')
			result.append(item)
		
		return result
		
		
	def episodes(self,page):
		result = []
		data = util.substr(page,self.od,self.do)
		pattern = '<img src="(?P<img>.+?)".+?/>[\s|\S]*?<a.+?href="(?P<url>.+?)">(?P<name>.+?)</a>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['title'] = m.group('name')
			item['url'] = m.group('url')
			item['img'] = m.group('img')
			result.append(item)
		return result
	
	def list(self,url):
		if url.find('#cat#') == 0:
                        return self.cat_det(util.request(self._url(url[5:])))
		if url.find('#film#') == 0:
                        return self.film(util.request(self._url(url[6:])))
		if url.find('#top#') == 0:
			self.od='<div class="content_box_nejpopul">'
			self.do='<div class="rozdeleni">Nejnovější</div>'
                        return self.episodes(util.request(self._url(url[:5])))
		if url.find('#new#') == 0:
			self.od='<div class="content_box_nejnovejsi">'
			self.do='<div class="rozdeleni">Top uživatelé</div>'
                        return self.episodes(util.request(self._url(url[:5])))
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
	

