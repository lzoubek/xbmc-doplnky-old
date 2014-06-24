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
import util
from provider import ContentProvider
import lxml.html

class SledujuserialyContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='.'):
        ContentProvider.__init__(self, 'sledujuserialy.cz', 'http://www.sledujuserialy.cz', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return [ 'resolve', 'cagetories', '!download' ]

    def categories(self):
        result = []
        for category in lxml.html.fromstring(urllib2.urlopen(self.base_url).read()) \
            .xpath('//div[@id="seznam_vyber"]/table/tr/td/div'):
            item = self.dir_item()
            item['title'] = category.text_content().encode('utf-8').strip('» ')
            url = category.xpath('./a')
            item['url'] = url[0].attrib['href'] if len(url) > 0 else '/'
            result.append(item)
        return result

    def list(self, url):
        if url.count('/') == 1:
            return self.list_series(url)
        return self.list_episodes(url)

    def list_series(self, url):
        result = []
        for serie in lxml.html.fromstring(urllib2.urlopen(self.base_url + url).read()) \
            .xpath('//div[@class="levy_blok"]/div'):
            item = self.dir_item()
            item['title'] = serie.text_content().encode('utf-8')
            item['url'] = re.findall(r'\'([^\']*)\'', serie.attrib['onclick'])[0]
            result.append(item)
        return result

    def list_episodes(self, url):
        result = []
        got_next = True
        while got_next:
            root = lxml.html.fromstring(urllib2.urlopen(self.base_url + url).read())
            for episode in root.xpath('//div[@class="pravy_blok"]/center/div[@class="nadpis"]/h2/a'):
                item = self.video_item()
                item['title'] = episode.text.encode('utf-8').strip()
                item['url'] = episode.attrib['href']
                item['img'] = re.findall(r'\([^)].*\)', episode.xpath('../../following-sibling::div[@class="uvodni_video"]')[0] \
                    .attrib['style'])[0].strip('()')
                result.append(item)
            for next in root.xpath('//div[@class="pravy_blok"]/center/table[@class="strankovanicko"]/tr/td/div[@class="strank_bg vice_pad"]/a'):
                if next.attrib['title'].encode('utf-8') == 'Dále':
                    url = next.attrib['href']
                    got_next = True
                    break
                got_next = False
        return result[::-1]

    def resolve(self, item, captcha_cb=None, select_cb=None):
        url = self._url(item['url'])
        data = util.substr(util.request(url), '<a name=\"video\"', '<div class=\"line_line')
        result = self.findstreams(data + url, [ '<embed( )src=\"(?P<url>[^\"]+)', '<object(.+?)data=\"(?P<url>[^\"]+)', '<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]', '<object.*?data=(?P<url>.+?)</object>' ])
        if len(result) == 1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return select_cb(result)
        return None
