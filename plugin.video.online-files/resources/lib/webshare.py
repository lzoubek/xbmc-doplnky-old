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
import re,urllib,urllib2,urlparse,cookielib,random,util,sys,os,traceback
from provider import ContentProvider
from provider import ResolveException
import elementtree.ElementTree as ET

class WebshareContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None,tmp_dir='.'):
        ContentProvider.__init__(self,'webshare.cz','http://webshare.cz/',username,password,filter,tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['search','resolve']

    def search(self,keyword):
        return self.list('what='+urllib.quote(keyword))

    def _create_request(self,url,base):
        args = dict(urlparse.parse_qsl(url))
        headers = {'X-Requested-With':'XMLHttpRequest','Accept':'text/xml; charset=UTF-8','Referer':self.base_url}
        req = base.copy()
        for key in req:
            if args.has_key(key):
                req[key] = args[key]
        return headers,req


    def list(self,url):
        result = []
        headers,req = self._create_request(url,{'what':'','offset':0,'limit':25,'category':'','sort':'','wst':''})
        data = util.post(self._url('api/search/'),req,headers=headers)
        xml = ET.fromstring(data)
        if not xml.find('status').text == 'OK':
            self.error('Server returned error status, response: %s' % data)
            return []
        total = int(xml.find('total').text)
        for file in xml.findall('file'):
            item = self.video_item()
            item['title'] = file.find('name').text
            item['url'] = 'ident=%s' % file.find('ident').text
            size = int(file.find('size').text)
            item['size'] = '%d MB' % (int(size)/1024/1024)
            img = file.find('img').text
            if img:
                item['img'] = self._url(img)
            self._filter(result,item)
        listed = int(req['limit']) + int(req['offset'])
        if total > listed:
            req['offset'] = listed
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = urllib.urlencode(req)
            result.append(item)
        return result


    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()        
        util.init_urllib()
        headers,req = self._create_request(item['url'],{'ident':''})
        data = util.post(self._url('api/file_link/'),req,headers=headers)
        xml = ET.fromstring(data)
        if not xml.find('status').text == 'OK':
            self.error('Server returned error status, response: %s' % data)
            raise ResolveException(xml.find('message').text)
        item['url'] = xml.find('link').text
        return item
