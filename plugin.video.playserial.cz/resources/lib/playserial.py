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

class PlayserialContentProvider(ContentProvider):

    od=''
    do=''

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'playserial.cz','http://playserial.eu/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['resolve','categories']


    def categories(self):
        result = []
	item = self.dir_item()
	item['type'] = 'new'
	item['url']  = '#new#'+self.base_url
	result.append(item)
        data = util.substr(util.request(self.base_url),'<ul>','</ul>')
        pattern = '<li><a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)' 
        for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		item = self.dir_item()
		item['title'] = m.group('name')
		item['url'] = '#cat#'+m.group('url')
		result.append(item)
        return result

    def episodes(self,page):
        result = []
        data = util.substr(page,'<div class=\'obsah\'>','</div>')
        pattern = '<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)' 
        for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		item = self.dir_item()
		item['title'] = m.group('name')
		item['url'] = '#show#'+m.group('url')
		self._filter(result,item)
        return result
    	
    def show(self,page):
        result = []
        data = util.substr(page,self.od,self.do)
        pattern='<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)'
        if self.do.find('</div>') == -1:
		pattern='(<b>(?P<serial>.+?)?</b> )'+pattern
        for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
		try:
			name = "[B]%s[/B] %s" % (m.group('serial'),m.group('name'))
		except:
			name = "%s" % (m.group('name'))
		item = self.video_item()
		item['url'] = m.group('url')
		item['title'] = name
		self._filter(result,item)
        return result
    
    
    def list(self,url):
        if url.find('#show#') == 0:
		self.od='<div class=\'obsah\''
		self.do='</div>'
		return self.show(util.request(self._url(url[6:])))
        if url.find('#new#') == 0:
		self.od='<h1><center>Naposledy přidáno: </center></h1>'
		self.do='<script language="JavaScript">'
		return self.show(util.request(self._url(url[:5])))
        if url.find('#cat#') == 0:
		return self.episodes(util.request(self._url(url[5:])))
        else:
		raise Expception("Invalid url, I do not know how to list it :"+url)


    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(url)
        data = util.substr(data,'<div class=\'obsah\'','</div>')
        resolved = resolver.findstreams(data,['[\"|\']+(?P<url>http://[^\"|\'|\\\]+)','flashvars=\"file=(?P<url>[^\"|\\\]+)','file=(?P<url>[^\&]+)'])
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



