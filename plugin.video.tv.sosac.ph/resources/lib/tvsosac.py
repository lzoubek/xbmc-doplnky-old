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

import re,os,urllib,urllib2,cookielib
import util

from provider import ContentProvider,cached,ResolveException

class TVSosacContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'tv.sosac.ph','http://tv.sosac.ph/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['resolve','categories']

    def categories(self):
        result = []
        for i in ['0-9','a','b','c','d','e','f','g','e','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']:
            item = self.dir_item()
            item['title'] = i.upper()
            item['url'] = 'cs/tv-shows-a-z/'+i
            result.append(item)
        return result

    def list(self,url):
        print url
        if url.find('tv-shows-a-z') >= 0:
            return self.list_shows_by_letter(url)
        if url.find('#serie#') == 0:
            return self.list_serie(url[7:])

    def list_serie(self,url):
        print url
        result = []
        page = util.request(self._url(url))
        data = util.substr(page,'<div class=\"content\">','<script')
        for s in re.finditer('<strong.+?</ul>',data,re.IGNORECASE | re.DOTALL):
            serie = s.group(0)
            serie_name = re.search('<strong>([^<]+)',serie).group(1)
            for e in re.finditer('<li.+?</li>',serie,re.IGNORECASE | re.DOTALL):
                episode = e.group(0)
                item = self.video_item()
                ep_name = re.search('<a href=\"#[^<]+<span>(?P<id>[^<]+)</span>(?P<name>[^<]+)',episode)
                if ep_name:
                    item['title'] = '%s %s %s' % (serie_name,ep_name.group('id'),ep_name.group('name'))
                i = re.search('<div class=\"inner-item[^<]+<img src=\"(?P<img>[^\"]+).+?<a href=\"(?P<url>[^\"]+)',episode, re.IGNORECASE | re.DOTALL)
                if i:
                    item['img'] = self._url(i.group('img'))
                    item['url'] = i.group('url')
                if i and ep_name:
                    self._filter(result,item)
        return result

    @cached(ttl=24*7)
    def list_shows_by_letter(self,url):
        result = []
        page = util.request(self._url(url))
        data = util.substr(page,'<ul class=\"content','</ul>') 
        for m in re.finditer('<a class=\"title\" href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL):
            item = self.dir_item()
            item['url'] = '#serie#'+m.group('url')
            item['title'] = m.group('name')
            self._filter(result,item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        page = util.request(item['url'])
        data = util.substr(page,'<div class=\"bottom-player\"','div>')
        if data.find('<iframe') < 0:
            raise ResolveException('Episoda jeste neni dostupna')
        result = self.findstreams(data,['<iframe src=\"(?P<url>[^\"]+)'])
        if len(result)==1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return select_cb(result)
