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
import re,urllib,urllib2,cookielib,random,util,sys,os,traceback,base64
from provider import ContentProvider

class BezvadataContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None,tmp_dir='.'):
        ContentProvider.__init__(self,'bezvadata.cz','http://bezvadata.cz/',username,password,filter,tmp_dir)
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
            page = util.request(self._url(ad.group('url')))
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


    def resolve(self,item,captcha_cb=None,wait_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        item['surl'] = url
        data = util.request(url)
        link = re.search('<a class="stahnoutSoubor.+?href=\"([^\"]+)',data)
        if link:
            url = self._url(link.group(1))
            data = util.request(url)
            m = re.search('<img src=\"(?P<img>[^\"]+)\" alt=\"Captcha\"',data)
            cap_id = re.search('<input type=\"hidden\" name=\"_uid_captcha.+?value=\"(?P<cid>[^\"]+)',data)
            if m and cap_id:
                cid = cap_id.group('cid')
                img_data = m.group('img')[m.group('img').find('base64,')+7:]
                if not os.path.exists(self.tmp_dir):
                    os.makedirs(self.tmp_dir)
                tmp_image = os.path.join(self.tmp_dir,'captcha.png')
                util.save_data_to_file(base64.b64decode(img_data),tmp_image)
                code = captcha_cb({'id':cid,'img': tmp_image})
                if not code:
                    return
                data = util.post(url+'?do=stahnoutFreeForm-submit',{'_uid_captcha':cid,'captcha':code,'stahnoutSoubor':'Stáhnout'})
                countdown = re.search('shortly\.getSeconds\(\) \+ (\d+)',data)
                last_url = re.search('<a class=\"stahnoutSoubor2.+?href=\"([^\"]+)',data)
                if countdown and last_url:
                    wait = int(countdown.group(1))
                    url = self._url(last_url.group(1))
                    wait_cb(wait)
                    req = urllib2.Request(url)
                    req.add_header('User-Agent',util.UA)    
                    resp = urllib2.urlopen(req)
                    item['url'] = resp.geturl()
                    return item

                    



