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

import re,os,urllib2,cookielib
import util,resolver

from provider import ContentProvider

class ReplayContentProvider(ContentProvider):

	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'re-play.cz','http://re-play.cz/category/videoarchiv/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','cagegories']


	def categories(self):
		return self.list(self.base_url)

	def list(self,url):
		result = []
		url = self._url(url)
		print url
		page = util.request(url)
		data = util.substr(page,'<div id=\"archive','end #archive')
		pattern = '<div class=\"cover\"><a href=\"(?P<url>[^\"]+)(.+?)title=\"(?P<name>[^\"]+)(.+?)<img src=\"(?P<logo>[^\"]+)(.+?)<p class=\"postmetadata\">(?P<fired>[^<]+)(.+?)<p>(?P<plot>[^<]+)'
		for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
			name = ('%s - %s' % (m.group('name'),m.group('fired').replace('/',''))).strip()
			item = self.video_item()
			item['title'] = name
			item['img'] = m.group('logo')
			item['plot'] = m.group('plot')
			item['url'] = m.group('url')
			self._filter(result,item)
	
		data = util.substr(page,'<div class=\"navigation\">','</div>')
		type = 'next'
		for m in re.finditer('<a href=\"(.+?)(?P<page>/page/[\d]+)',data,re.IGNORECASE | re.DOTALL):
			item = self.dir_item()
			item['type'] = type
			if type == 'next':
				type = 'prev'
			item['url'] = m.group('page')
			result.append(item)
		return result

	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		data = util.substr(util.request(url),'<div class=\"zoomVideo','</div>')
		resolved = resolver.findstreams(data,['<object(.+?)data=\"(?P<url>http\://www\.youtube\.com/v/[^\&]+)'])
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

