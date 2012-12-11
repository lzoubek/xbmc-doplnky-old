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
		ContentProvider.__init__(self,'hejbejse.tv','http://www.kynychova.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories']
		
		
	def categories(self):
		result = []
		#
		data = util.substr(util.request(self.base_url+'index.php?id=17'),'<div id="sidebar">','</div>')
		pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)' 
		for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
			item = self.video_item()
			item['title'] = m.group('name')
			item['url'] = m.group('url')
			result.append(item)
		return result
		
                       
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		data = util.request(url)
		data = util.substr(data,'<div id="content">','<div class="clear">')
		resolved = resolver.findstreams(data,['flash[V|v]ars=\"(?P<url>id=.+?)\" ','<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
                result = []
                try:
			for i in resolved:
				item = self.video_item()
				item['title'] = i['name']
				item['url'] = i['url']
				item['quality'] = i['quality']
				item['surl'] = i['surl']
				result.append(item)  
		except:
			print '===Unknown resolver==='
			
                if len(result)==1:
                        return result[0]
                elif len(result) > 1 and select_cb:
                        return select_cb(result)
