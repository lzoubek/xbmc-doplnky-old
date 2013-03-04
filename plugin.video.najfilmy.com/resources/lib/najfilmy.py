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

class NajfilmyContentProvider(ContentProvider):
	
	od=''
	do=''

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'najfilmy.cz','http://www.naj-filmy.com/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['search','categories']
		
	def getInfo(self,link):
		data = util.request(link)
		data = util.substr(data,'<p id=\"file_rating\">','<div class=\"clear\">')
		pattern = 'id=\"file_rating\">(?P<rating>.+?)</p>[\s|\S]*?<p>(?P<info>.+?)</p>[\s|\S]*?<p class=\"file_info\">Přidáno: (?P<date>.+?)</p>'
		m = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			return m.group('rating'),m.group('info'),m.group('date')
		else:
			return '','',''

	def search(self,keyword):
		self.od='<div id=\"content\" class=\"narrowcolumn\">'
		self.do='<div class=\"navigation\">'
                return self.film(util.request(self._url('?s='+keyword)))
		
			
	def film(self,page):
		result=[]
		
		data = util.substr(page,self.od,self.do)
		pattern='background: url\((?P<img>.+?)\)[\s|\S]*?<h2><a href=\"(?P<url>.+?)\".[^>]+>(?P<name>.+?)</a></h2>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['url'] = m.group('url')
			item['title'] = m.group('name')
			item['img'] = m.group('img')
			result.append(item)
		data = util.substr(page,'<div class=\'wp-pagenavi\'>','<div id=\"sidebar\">')
		pattern='<span class=\'pages\'>(?P<pg>.+?)</span>'
		m = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
		last_page=''
		if not m == None:
			last_page=m.group('pg').split(' ')
			next_page=int(last_page[1])+1
			last_page=last_page[-1]
		
		pattern = 'href=\"(?P<url>.+?)\".?><div class=\"next"></div>'
		m = re.search(pattern, data, re.IGNORECASE | re.DOTALL)
		next_url=''
		if not m == None:
			next_url=m.group('url')
			try:	
				item = self.dir_item()
				item['title'] = 'Přejít na stranu '+ str(next_page)+' z '+ str(last_page)
				item['url'] = '#film#'+next_url
				result.append(item)
			except:
				pass
		
		return result

	
	def categories(self):
		result = []
		
		item = self.dir_item()
		item['type'] = 'new'
		item['url']  = '#last#'+self.base_url
		result.append(item)
		
		item=self.dir_item()
		item['title']='Kategorie filmů'
		item['url']  = '#cat#'+self.base_url
		result.append(item)

		item=self.dir_item()
		item['title']='Filmy'
		item['url']  = '#film#'+self._url('filmy/')
		result.append(item)
		
		item=self.dir_item()
		item['title']='Serialy'
		item['url']  = '#serial#'+self._url('serialy/')
		result.append(item)
		
		return result
		
	def episodes(self,page):
		result = []
		data = util.substr(page,self.od,self.do)
		pattern='value=\"(?P<url>.+?)\">(?P<name>.+?)</option>'
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.dir_item()
			item['title']=m.group('name').replace('&nbsp;','')
			item['url'] = '#film#'+m.group('url')
			result.append(item)
		return result
		
	
	def list(self,url):
		if url.find('#film#') == 0:
			self.od='<div id=\"content\" class=\"narrowcolumn\">'
			self.do='<div class=\"navigation\">'
                        return self.film(util.request(self._url(url[6:])))
		if url.find('#serial#') == 0:
			self.od='<select name=\'gdtt-drop-gdtttermslist3'
			self.do='</select>'
                        return self.episodes(util.request(self._url(url[8:])))
		if url.find('#cat#') == 0:
			self.od='<select name=\'gdtt-drop-gdtttermslist4'
			self.do='</select>'
                        return self.episodes(util.request(self._url(url[5:])))
		if url.find('#last#') == 0:
			self.od='<div id=\"content\" class=\"narrowcolumn\">'
			self.do='<div class=\"navigation\">'
                        return self.film(util.request(self._url(url[6:])))
		else:
                        raise Expception("Invalid url, I do not know how to list it :"+url)

                        
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		#print 'URL: '+url
		hdata = util.request(url)
		
		data = util.substr(hdata,'<div class=\"AWD_like_button','<div class=\"postmetadata\">')
		
			
		resolved = resolver.findstreams(data,['flash[V|v]ars=\"(?P<url>id=.+?)\" ','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=["|\'](?P<url>.+?)["|\']','href="(?P<url>http://(www.)?streamcloud\.eu.+?)"'])
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
	

