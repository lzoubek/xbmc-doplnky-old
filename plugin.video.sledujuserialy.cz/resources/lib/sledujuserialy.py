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
import urllib2,re,os,sys,cookielib
import util,resolver
from provider import ContentProvider

class SledujuserialyContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None,tmp_dir='.'):
        ContentProvider.__init__(self,'sledujuserialy.cz','http://www.sledujuserialy.cz/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['resolve','cagegories']


    def categories(self):
        result = []
#		item = self.dir_item()
#		item['type'] = 'new'
#		item['url'] = 'category/new-episode'
#		result.append(item)
        page = util.request(self.base_url)
        data = util.substr(page,'<h2 class=\"vyber_serialu','<div class=\"levy_blok')
        pattern='<div.+?class=\"menu_click\" onclick=\"[^\']+\'(?P<url>[^\']+).+?<div.+?class=\"menu_sipecka\">[^>]+>(?P<name>[^<]+)'	
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            item = self.dir_item()
            item['title'] = m.group('name').decode('windows-1250').encode('utf-8').strip()
            item['url'] = m.group('url')
            result.append(item)
        return result


    def list(self,url):
        result = []
        page = util.request(self._url(url))
        data = util.substr(page,'<div class=\"pravy_blok\"','<div class=\"paticka')
        pattern = '<div style=\"background-image\: url\((?P<img>[^\)]+)[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<img.+?title=\"(?P<name>[^\"]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            item['title'] = m.group('name').decode('windows-1250').encode('utf-8')
            item['url'] = m.group('url')
            item['img'] = self._url(m.group('img'))
            self._filter(result,item)
        next = re.search(u'<a href=\"(?P<url>[^\"]+)\" title=\"Dále\"',data)
        if next:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = next.group('url')
            result.append(item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.substr(util.request(url),'<a name=\"video\"','<div class=\"line_line')
        resolved = resolver.findstreams(data+url,['<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
        result = []
        if not resolved:
            util.info('Nothing resolved :-(')
            return
        for i in resolved:
            item = self.video_item()
            item['title'] = i['name']
            item['url'] = i['url']
            item['quality'] = i['quality']
            item['surl'] = i['surl']
            item['subs'] = i['subs']
            result.append(item)     
        if len(result)==1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return select_cb(result)


