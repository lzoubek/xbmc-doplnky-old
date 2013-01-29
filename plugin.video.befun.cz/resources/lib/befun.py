# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Libor Zoubek
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

import re,os,urllib,urllib2,shutil,traceback,cookielib
import util,resolver
from provider import ContentProvider

class BefunContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'befun.cz','http://befun.cz/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories','resolve','search']

    def search(self,keyword):
        return self.list_page('vyhledat/results?q='+keyword+'&c=filmy','<h2>Výsledky vyhledávání</h2>','</section')

    def list(self,url):
        return self.list_page(url,'<!-- Movies','</section')

    def list_page(self,url,start,end):
        page = util.request(self._url(url))
        next = re.search('<a href=\"(?P<url>[^\"]+)\" class=\"ajax\">Další',page)
        page = util.substr(page,start,end)
        result = []
        for m in re.finditer('<article[^>]+(.+?)</article>',page,re.IGNORECASE|re.DOTALL):
            data =  m.group(1)
            url = re.search('<a href=\"([^\"]+)',data)
            img = re.search('<img src=\"(?P<img>[^\"]+).+?alt=\"(?P<name>[^\"]+)',data)
            if img and url:
                item = self.video_item()
                item['url'] = url.group(1)
                item['img'] = self._url(img.group('img'))
                item['title'] = img.group('name')
                self._filter(result,item)
        if next:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = next.group('url')
            result.append(item)
        return result

    def categories(self):
        data = util.request(self.base_url)
        data = util.substr(data,'<ul id=\"menu_kategorie','</ul')
        result = []
        
        for m in re.finditer('<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
            item = self.dir_item()
            item['title'] = m.group('name')
            item['url'] = m.group('url')
            result.append(item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(self._url(item['url']))	
        data = util.substr(data,'<div class=\"video','</div')
        sosac = re.search('\"(http\://movies\.sosac\.ph[^\"]+)',data,re.DOTALL)
        if sosac:
            data = util.request(sosac.group(1))
        resolved = resolver.findstreams(data,[
            '<embed( )*flashvars=\"file=(?P<url>[^\"]+)',
            '<embed( )src=\"(?P<url>[^\"]+)',
            '<object(.+?)data=\"(?P<url>[^\"]+)',
            '<iframe(.+?)src=[\"\' ](?P<url>.+?)[\'\" ]',
            ])
        result = []
        if not resolved:
            self.error('Nothing resolved')
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
