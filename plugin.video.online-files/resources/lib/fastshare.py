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
from provider import ResolveException

class FastshareContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None,tmp_dir='.'):
        ContentProvider.__init__(self,'fastshare.cz','http://www.fastshare.cz/',username,password,filter,tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['search','resolve']

    def search(self,keyword):
        return self.list('?term='+urllib.quote(keyword))

    def list(self,url):
        result = []
        page = util.request(self._url(url))
        data = util.substr(page,'<div class=\"search','<footer')
        for m in re.finditer('<div class=\"search-result-box(.+?)</a>',data,re.IGNORECASE | re.DOTALL ):
            it = m.group(1)
            link = re.search('<a href=([^ ]+)',it,re.IGNORECASE | re.DOTALL)
            name = re.search('title=\"([^\"]+)',it,re.IGNORECASE | re.DOTALL)
            img = re.search('<img src=\"([^\"]+)',it,re.IGNORECASE | re.DOTALL)
            size = re.search('<div class=\"fs\">([^<]+)',it,re.IGNORECASE | re.DOTALL)
            time = re.search('<div class=\"vd\">([^<]+)',it,re.IGNORECASE | re.DOTALL)
            if name and link:
                item = self.video_item()
                item['title'] = name.group(1)
                if size:
                    item['size'] = size.group(1).strip()
                if time:
                    item['length'] =  time.group(1).strip()
                item['url'] = self._url(link.group(1))
                item['img'] = self._url(img.group(1))
                self._filter(result,item)
        next = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>dal',data,re.IGNORECASE | re.DOTALL) 
        if next:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = next.group('url')
            result.append(item)
        return result


    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()        
        util.init_urllib()
        url = self._url(item['url'])
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            page = response.read()
            response.close()
        except urllib2.HTTPError, e:
            traceback.print_exc()
            return
        data = util.substr(page,'<form method=post target=\"iframe_dwn\"','</form>')
        action = re.search('action=(?P<url>[^>]+)',data,re.IGNORECASE | re.DOTALL)
        img = re.search('<img src=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
        if img and action:
            sessid=[]
            for cookie in re.finditer('(PHPSESSID=[^\;]+)',response.headers.get('Set-Cookie'),re.IGNORECASE | re.DOTALL):
                sessid.append(cookie.group(1))
            # we have to download image ourselves
            image = util.request(self._url(img.group('url')),headers={'Referer':url,'Cookie':sessid[-1]})
            img_file = os.path.join(self.tmp_dir,'captcha.png')
            util.save_data_to_file(image,img_file)
            code = None
            if captcha_cb:
                code = captcha_cb({'id':'0','img':img_file})
            if not code:
                self.info('No captcha received, exit')
                return
            request = urllib.urlencode({'code':code})
            req = urllib2.Request(self._url(action.group('url')),request)
            req.add_header('User-Agent',util.UA)
            req.add_header('Referer',url)
            req.add_header('Cookie',sessid[-1])
            try:
                resp = urllib2.urlopen(req)
                file_url = resp.geturl()
                if file_url.find(action.group('url')) > 0:            
                    msg = resp.read()
                    resp.close()
                    js_msg = re.search('alert\(\'(?P<msg>[^\']+)',msg,re.IGNORECASE | re.DOTALL)
                    if js_msg:
                        raise ResolveException(js_msg.group('msg'))
                    raise ResolveException('')
                resp.close()
                if file_url.find('data') >=0 or file_url.find('download_free') > 0:
                    item['url'] = file_url
                    return item
                self.error('wrong captcha, retrying')
                return self.resolve(item,captcha_cb,select_cb)
            except urllib2.HTTPError:
                traceback.print_exc()
                return
