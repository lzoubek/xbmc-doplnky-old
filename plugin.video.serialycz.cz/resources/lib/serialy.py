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
import urllib2,re,os,md5,sys,cookielib
import util,resolver
from provider import ContentProvider

class SerialyczContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None,tmp_dir='.'):
        ContentProvider.__init__(self,'serialycz.cz','http://www.serialycz.cz/',username,password,filter,tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['resolve','cagegories']


    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = 'category/new-episode'
        result.append(item)
        data = util.substr(util.request(self.base_url),'<div id=\"primary\"','</div>')
        pattern='<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
        for m in re.finditer(pattern, util.substr(data,'Seriály</a>','</ul>'), re.IGNORECASE | re.DOTALL):
            image,plot = self._get_meta(m.group('name'),m.group('url'))
            item = self.dir_item()
            item['title'] = m.group('name')
            item['url'] = m.group('url')
            item['img'] = image
            item['plot'] = plot
            result.append(item)
        return result

    def _get_meta(self,name,link):
        # load meta from disk or download it (slow for each serie, thatwhy we cache it)
        local = self.tmp_dir
        if not os.path.exists(local):
            os.makedirs(local)
        m = md5.new()
        m.update(name)
        image = os.path.join(local,m.hexdigest()+'_img.url')
        plot = os.path.join(local,m.hexdigest()+'_plot.txt')
        if not os.path.exists(image):
            data = util.request(link)
            data = util.substr(data,'<div id=\"archive-posts\"','</div>')
            m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
            if not m == None:
                data = util.request(m.group('url'))
                self._get_image(data,image)
                self._get_plot(data,plot)
        return util.read_file(image).strip(),util.read_file(plot)

    def _get_plot(self,data,local):
        data = util.substr(data,'<div class=\"entry-content\"','</p>')
        m = re.search('<(strong|b)>(?P<plot>(.+?))<', data, re.IGNORECASE | re.DOTALL)
        if not m == None:
            util.save_data_to_file(util.decode_html(m.group('plot')).encode('utf-8'),local)

    def _get_image(self,data,local):
        data = util.substr(data,'<div class=\"entry-photo\"','</div>')
        m = re.search('<img(.+?)src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
        if not m == None:
            util.save_data_to_file(m.group('img'),local)


    def new_episodes(self,page):
        result = []
        data = util.substr(page,'<div id=\"archive-posts\"','</ul>')
        pattern='<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            name = util.decode_html(m.group('name'))
            item = self.video_item()
            item['url'] = m.group('url')
            item['title'] = name
            item['img'] = m.group('img')
            self._filter(result,item)
        return result

    def list(self,url):
        if url.find('category/new-episode') == 0:
            return self.new_episodes(util.request(self._url(url)))
        result = []
        page = util.request(self._url(url))
        data = util.substr(page,'<div id=\"archive-posts\"','</div>')
        m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
        if m:
            data = util.request(m.group('url'))
            for m in re.finditer('<a href=\"(?P<url>[^\"]+)(.+?)(<strong>|<b>)(?P<name>[^<]+)', util.substr(data,'<div class=\"entry-content','</div>'), re.IGNORECASE | re.DOTALL):
                item = self.video_item()
                item['title'] = util.decode_html(m.group('name'))
                item['url'] = m.group('url')
                self._filter(result,item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url']).replace('×','%c3%97')
        data = util.substr(util.request(url),'<div id=\"content\"','#content')
        resolved = resolver.findstreams(data,['<embed( )src=\"(?P<url>[^\"]+)','<object(.+?)data=\"(?P<url>[^\"]+)','<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
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


