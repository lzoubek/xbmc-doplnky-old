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

class HejbejseContentProvider(ContentProvider):
	
	od=''
	do=''

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'hejbejse.tv','http://www.hejbejse.tv/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','cagegories']
		
		
	def categories(self):
		result = []
		item=self.dir_item()
		item['title']='[B]Oblíbená videa[/B]'
		item['url']  = '#pop#'+self.base_url
		result.append(item)
		#
		item=self.dir_item()
		item['title']='[B]Poslední videa[/B]'
		item['url']  = '#last#'+self.base_url
		result.append(item)
		#

		data = util.substr(util.request(self.base_url),'</b> PROGRAMY</h3>','<div class="clear">')
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.dir_item()
			item['title'] = m.group('name')
			item['url'] = '#cat#'+m.group('url')
			result.append(item)
		return result
		
	def episodes(self,page):
		result = []
		data = util.substr(page,self.od,self.do)
		pattern = '<a href=\"(?P<url>.+?)\"[\s|\S]*?<img.*?src=\"(?P<img>.+?)\"[\s|\S]*?<strong[^>]+>(?P<name>.*?)</strong>' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			if (m.group('name')==''): 
				name='---'
			else:
				name=m.group('name')
			
			item = self.video_item()
			#item['title'] = m.group('name')
			item['title'] = name
			item['url'] = m.group('url')
			item['img'] = self._url(m.group('img'))
			self._filter(result,item)
		return result

	
	def list(self,url):
		if url.find('#cat#') == 0:
			self.od='<h3 class=\"title\"><b>hejbejseTV</b> </h3>'
			self.do='</table>'
                        return self.episodes(util.request(self._url(url[5:])))
		if url.find('#pop#') == 0:
			self.od='</b> Oblíbená videa</h3>'
			self.do='</table>'
                        return self.episodes(util.request(self._url(url[:5])))
		if url.find('#last#') == 0:
			self.od='</b> Poslední videa</h3>'
			self.do='</table>'
                        return self.episodes(util.request(self._url(url[:6])))
		else:
                        raise Expception("Invalid url, I do not know how to list it :"+url)

                        
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		hdata = util.request(url)
		
		data = util.substr(hdata,'<div class="content_scroller">','<p>')
		name = 'Film'
		for m in re.finditer('<h2>(?P<name>.+?)</h2>',data,re.IGNORECASE | re.DOTALL ):
			name = "%s" % (m.group('name'))
		
		data = util.substr(hdata,'function startVideo','plugins: ')
		resolved = resolver.findstreams(data,['url:.*\"(?P<url>.+?)\",'])
		
                result = []
		for i in resolved:
                        item = self.video_item()
                        #item['title'] = i['name']
                        item['title'] = name
                        item['url'] = i['url'].replace(' ','%20')
                        item['quality'] = i['quality']
                        item['surl'] = i['surl']
                        result.append(item)  
                if len(result)==1:
                        return result[0]
                elif len(result) > 1 and select_cb:
                        return select_cb(result)
	

