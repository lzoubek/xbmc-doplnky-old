# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2012 Libor Zoubek
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
import re,urllib,urllib2,cookielib,random,util,sys,os,traceback
from provider import ContentProvider

class KoukniContentProvider(ContentProvider):

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'koukni.cz','http://koukni.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['search','resolve','cagegories']

	def search(self,keyword):
		return self.list('hledej?hledej='+urllib.quote(keyword))

	def categories(self):
		result = []
		
		item = self.dir_item()
		item['type'] = 'new'
		item['url'] = self._url('new')
		result.append(item)
		
		item = self.dir_item()
		item['type'] = 'top'
		item['url'] = self._url('nej')
		result.append(item)

		for cat in ['clipz','Wa4lock','minno','USA','simpsons','serialz','znovy','zoufalky','vypravej','topgear','COWCOOSH']:
			item = self.dir_item()
			item['title'] = cat
			item['url'] = self._url(cat)
			result.append(item)
		return result
		
	def list(self,url):
		result = []
		data = util.request(self._url(url))
		for m in re.finditer('<div class=\"row\"(.+?)<a href=\"(?P<url>[^\"]+)(.+?)src=\"(?P<logo>[^\"]+)(.+?)<h1>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['title'] = m.group('name')
			item['img'] = self._url(m.group('logo'))
			item['url'] = m.group('url')
			self._filter(result,item)
		navurl = url
		index = url.find('?')
		if index > 0:
			navurl = url[:index]
	
		prev = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/predchozi.png',data,re.IGNORECASE | re.DOTALL )
		if prev:
			item = self.dir_item()
			item['type'] = 'prev'
			item['url'] = navurl+prev.group('url')
			result.append(item)
		next = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/dalsi.png',data,re.IGNORECASE | re.DOTALL )
		if next:
			item = self.dir_item()
			item['type'] = 'next'
			item['url'] = navurl+next.group('url')
			result.append(item)
		return result



	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		data = util.request(url)
		video = re.search('=\"player\" href=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
		subs = re.search('captionUrl\: \'(?P<url>[^\']+)',data,re.IGNORECASE | re.DOTALL)
		if video:
			req = urllib2.Request(self._url(video.group('url')))
			req.add_header('User-Agent',util.UA)
			response = urllib2.urlopen(req)
			response.close()
			item['url'] = response.geturl()
			item['surl'] = url
			item['quality'] = '720p'
			if subs:
				item['subs'] = self._url(subs.group('url'))
			return item
