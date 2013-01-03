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

import re,os,urllib,urllib2,shutil,traceback,cookielib
import util,resolver
from provider import ContentProvider

class EserialContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'eserial.cz','http://eserial.cz/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories','resolve']

    def show(self,url):
        data = util.request(self._url(url))
        data = util.substr(data,'<menu>','</menu>')
        result = []
        for m in re.finditer('<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
            item = self.dir_item()
            item['title'] = m.group('name')
            item['url'] = '#list#'+m.group('url')
            if self.filter:
                if self.filter(item):
                    result.append(item)
            else:
                result.append(item)
        return result

    def episodes(self,url):
        data = util.request(self._url(url))
        result = []
        print url
        for m in re.finditer('<div class=\'dily-vypis\'>(?P<show>.+?)</div>',data,re.IGNORECASE | re.DOTALL ):
            show = m.group('show')
            link = re.search('<a href=\'(?P<url>[^\']+)[^<]+<img src=(?P<img>[^ ]+)[^<]+</a>.+?<div[^<].+?<a[^>]+>(?P<index>[^<]+)<b>(?P<name>[^<]+)',show)
            if link:
                vurl = link.group('url')
                name = link.group('index') + link.group('name')
                item = self.video_item()
                item['title'] = name
                item['url'] = vurl
                item['img'] = self._url(link.group('img').strip('\'\"'))
                self._filter(result,item)
        return result

    def new(self,url):
        data = util.request(self._url(url))
        result = []
        data = util.substr(data,'<head>','</body>')
        for m in re.finditer('<div class=\'dily-vypis\'>(?P<ep>.+?)</center>',data,re.IGNORECASE | re.DOTALL ):
            ep = m.group('ep')
            link = re.search('<a href=\'(?P<url>[^\']+)[^<]+<img src=(?P<img>[^ ]+)[^<]+</a>.+?<center>(?P<name>[^<]+)<div[^<]+</div><img[^>]+>(?P<name2>[^<]+).+?<a href=\'(?P<surl>[^\'])[^>]*>(?P<sname>[^<]+)',ep)
            if link:
                name = '%s - %s %s' % (link.group('sname'),link.group('name2'),link.group('name'))
                item = self.video_item()
                item['title'] = name
                item['url'] = link.group('url')
                item['img'] = self._url(link.group('img').strip('\'\"'))
                item['show'] = link.group('sname').strip()
                item['epid'] = link.group('name2')
                item['epname'] = link.group('name')
                print item
                self._filter(result,item)
        return result


    def list(self,url):
        if url.find('#show#') == 0:
            return self.show(url[6:])
        if url.find('#list#') == 0:
            return self.episodes(url[6:])
        if url.find('#new#') == 0:
            return self.new(url[5:])
        else:
            raise Expception("Invalid url, I do not know how to list it :"+url)

    def categories(self):
        data = util.request(self.base_url)
        data = util.substr(data,'<div id=\"stred','</center>')
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = '#new#himym/novinky'
        result.append(item)
        
        for m in re.finditer('<a href=\'(?P<url>[^\']+)[^<]+<img src=(?P<img>[^ ]+)[^<]+</a>[^<]*<div[^<]*<a[^>]+>(?P<name>[^<]+)',data,re.IGNORECASE | re.DOTALL ):
            item = self.dir_item()
            item['img'] = self._url(m.group('img').strip('\'\"'))
            item['title'] = m.group('name')
            item['url'] = '#show#'+m.group('url')
            result.append(item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(self._url(item['url']))	
        data = util.substr(data,'<div id=\"stred','<div id=\'patka>')
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
