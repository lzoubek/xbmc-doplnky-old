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

import re,os,urllib,urllib2,cookielib
import util,resolver

from provider import ContentProvider

class NastojakaContentProvider(ContentProvider):

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'nastojaka.cz','http://www.nastojaka.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['search','resolve','cagegories']

	def search(self,keyword):
		data = util.post(self.base_url+'vyhledavani',{'btnsearch':'OK','txtsearch':keyword});
		return self.show(data)

	def categories(self):
		result = []
		
		item = self.dir_item()
		item['title'] = '$30005'
		item['url'] = 'scenky/?sort=date'
		result.append(item)
		
		item = self.dir_item()
		item['title'] = '$30006'
		item['url'] = 'scenky/?sort=performer'
		result.append(item)

		item = self.dir_item()
		item['title'] = '$30007'
		item['url'] = 'scenky/?sort=rating'
		result.append(item)
		return result
		
	def list(self,url):
		return self.show(util.request(self._url(url)))


	def show(self,page):
		result = []
		data = util.substr(page,'<div id=\"search','<hr>')
		for m in re.finditer('<div.+?class=\"scene[^>]*>.+?<img src="(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+).+?<div class=\"sc-name\">(?P<author>[^<]+).+?<a href=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL ):
			name = "%s (%s)" % (m.group('name'),m.group('author'))
			item = self.video_item()
			item['title'] = name
			item['url'] = m.group('url')
			item['img'] = m.group('img')
			if self.filter:
				if self.filter(item):
					result.append(item)
			else:
				result.append(item)
	
		data = util.substr(page,'class=\"pages\">','</div>')
		next = re.search('<a href=\"(?P<url>[^\"]+)\"[^<]+<img src=\"/images/page-right.gif',data)
		prev = re.search('<a href=\"(?P<url>[^\"]+)\"[^<]+<img src=\"/images/page-left.gif',data)
		if prev:
			item = self.dir_item()
			item['type'] = 'prev'
			item['url'] = prev.group('url')
			result.append(item)
		if next:
			item = self.dir_item()
			item['type'] = 'next'
			item['url'] = next.group('url')
			result.append(item)
		return result

	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		data = util.request(url)
		data = util.substr(data,'<div class=\"video','</div>')
		resolved = resolver.findstreams(data,['<embed( )src=\"(?P<url>[^\"]+)'])
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
		return

