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

class BezvadataContentProvider(ContentProvider):

	def __init__(self,username=None,password=None,filter=None):
		self.name='bezvadata'
		self.username=username
		self.password=password
		self.filter = filter
		self.base_url='http://bezvadata.cz/'
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['search','resolve']

	def search(self,keyword):
		return self.list('vyhledavani/?s='+urllib.quote(keyword))

		
	def list(self,url):
		page = util.request(self._url(url))
		ad = re.search('<a href=\"(?P<url>/vyhledavani/souhlas-zavadny-obsah[^\"]+)',page,re.IGNORECASE|re.DOTALL)
		if ad:
			page = util.request(furl(ad.group('url')))
		data = util.substr(page,'<div class=\"content','<div class=\"stats')
		pattern = '<section class=\"img[^<]+<a href=\"(?P<url>[^\"]+)(.+?)<img src=\"(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+)(.+?)<b>velikost:</b>(?P<size>[^<]+)'
		result = []
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['title'] = m.group('name')
			item['size'] = m.group('size').strip()
			item['img'] = m.group('img')
			item['url'] = m.group('url')
			# mark 18+ content
			if ad:
				item['18+'] = True
			if self.filter:
				if self.filter(item):
					result.append(item)
			else:
				result.append(item)

		# page navigation
		data = util.substr(page,'<div class=\"pagination','</div>')
		m = re.search('<li class=\"previous[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
		if m:
			item = self.dir_item()
			item['type'] = 'prev'
			item['url'] = m.group('url')
			result.append(item)
		n = re.search('<li class=\"next[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
		if n:
			item = self.dir_item()
			item['type'] = 'next'
			item['url'] = n.group('url')
			result.append(item)
		return result


	def resolve(self,item,captcha_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		data = util.request(url)
		request = urllib.urlencode({'stahnoutSoubor':'Stáhnout'})
		req = urllib2.Request(url+'?do=stahnoutForm-submit',request)
		req.add_header('User-Agent',util.UA)	
		resp = urllib2.urlopen(req)
		item['url'] = resp.geturl()
		item['surl'] = url
		return item
