# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2012 Lubomir Kucera
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
import urllib2,urllib,re,os,sys,cookielib
import util
from provider import ContentProvider
import lxml.html
import urlparse
import cgi

class TeeveeContentProvider(ContentProvider):

    urls = { 'Filmy' : 'http://www.filmy.teevee.sk', 'Seriály' : 'http://www.teevee.sk' }

    def __init__(self, username=None, password=None, filter=None, tmp_dir='.'):
        ContentProvider.__init__(self, 'teevee.sk', 'http://www.teevee.sk', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return [ 'resolve', 'cagetories', 'search' ]

    def categories(self):
        result = []
        for category in self.urls.keys():
            item = self.dir_item()
            item['title'] = category
            item['url'] = self.urls[category]
            result.append(item)
        return result

    def search(self, keyword):
        result = []
        for category in self.urls.keys():
            for result_item in lxml.html.parse(self.urls[category] + '/ajax/_search_engine.php?search=' +
                urllib.quote_plus(keyword) + ('&film=1' if category == 'Filmy' else '')).xpath('//a'):
                if 'href' in result_item.attrib:
                    item = self.video_item()
                    item['title'] = result_item.text.encode('Latin1')
                    item['url'] = result_item.attrib['href']
                    result.append(item)
        return result

    def list(self, url):
        if '.filmy.' in url:
            if url.count('&') == 0:
                return self.list_movies(url + '/ajax/_filmTable.php?showmore=1&strana=1')
            return self.list_movies(url)
        else:
            if url.count('/') == 2:
                return self.list_series(url + '/ajax/_serials_list.php')
            elif url.count('/') == 4 and url.count('&') == 0:
                return self.list_seasons(url)
            return self.list_episodes(url)

    def list_movies(self, url):
        result = []
        for movie in lxml.html.parse(url).xpath('//a[span]'):
            item = self.video_item()
            item['title'] = movie.text.encode('Latin1')
            dates = movie.xpath('./span[@class="date"]')
            if len(dates) > 0:
                item['title'] += ' ' + dates[0].text.encode('Latin1')
            item['url'] = movie.attrib['href']
            result.append(item)
        params = urlparse.parse_qs(urlparse.urlparse(url).query)
        parts = list(urlparse.urlsplit(url))
        d = dict(cgi.parse_qsl(parts[3]))
        d.update(strana = (str(int(params['strana'][0]) + 1) if 'strana' in params else '1'))
        parts[3] = urllib.urlencode(d)
        url = urlparse.urlunsplit(parts)
        if len(lxml.html.parse(url).xpath('//a/span')) > 0:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = url
            result.append(item)
        return result

    def list_series(self, url):
        result = []
        for serie in lxml.html.parse(url).xpath('//table/tr/td/a'):
            item = self.dir_item()
            item['title'] = serie.text.encode('Latin1')
            item['url'] = url + '?serial_id=' + serie.attrib['href'].split('/')[-1]
            result.append(item)
        return result

    def list_seasons(self, url):
        result = []
        for serie_i, serie in enumerate(lxml.html.parse(url).xpath('//div[@class="se"]/a')):
            item = self.dir_item()
            item['title'] = serie.text.encode('Latin1')
            item['url'] = url + '&seria_id=' + str(serie_i + 1)
            result.append(item)
        return result

    def list_episodes(self, url):
        result = []
        for serie in lxml.html.parse(url).xpath('//div/div/a'):
            item = self.video_item()
            item['title'] = serie.text.encode('Latin1')
            item['url'] = serie.attrib['href']
            result.append(item)
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
        data = ''
        for server in lxml.html.parse(item['url']).xpath('//div[@id="menuServers"]/a'):
            data += util.request('/'.join(item['url'].split('/')[:3]) +
                '/ajax/_change_page.php?stav=changeserver&server_id=' + server.attrib['href'].strip('#'))
        result = self.findstreams(data + item['url'], [ '<embed( )src=\"(?P<url>[^\"]+)', '<object(.+?)data=\"(?P<url>[^\"]+)',
            '<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]', '<object.*?data=(?P<url>.+?)</object>' ])
        if len(result) == 1:
            return result[0]
        elif len(result) > 1:
            return select_cb(result)
        return None