# -*- coding: UTF-8 -*-
# /*
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

import re
import urllib
import urllib2
import cookielib
from xml.etree.cElementTree import fromstring

import util
import resolver
from provider import ResolveException
from provider import ContentProvider

class VideaceskyContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'videacesky.cz', 'http://www.videacesky.cz', username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories', 'resolve', 'search']

    def list(self, url):
        if url.find('#top10#') == 0:
            return self.list_top10(util.request(self.base_url))
        else:
            return self.list_content(util.request(self._url(url)), self._url(url))
        
    def search(self, keyword):
        return self.list('?s=' + urllib.quote(keyword))
        
    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = "?orderby=post_date"
        result.append(item)
        item = self.dir_item()
        item['type'] = 'top'
        item['url'] = "?r_sortby=highest_rated"
        result.append(item)
        item = self.dir_item()
        item['title'] = 'TOP 10 měsíce'
        item['url'] = "#top10#"
        result.append(item)
        data = util.request(self.base_url)
        data = util.substr(data, '<ul id=\"headerMenu2\">', '</ul>')
        pattern = '<a href=\"(?P<url>[^\"]+)(.+?)>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            if m.group('url') == '/':
                continue
            item = self.dir_item()
            item['title'] = m.group('name')
            item['url'] = m.group('url')
            result.append(item)
        return result
    
    
    def list_top10(self, page):
        result = []
        data = util.substr(page, 'TOP 10 měsíce', 'class=\"sidebarBox widget_text\"')
        pattern = '<li><a href=\"(?P<url>[^"]+)\" title=\"(?P<title>[^"]+)\"(.+?)</li>'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            item['title'] = m.group('title')
            item['url'] = m.group('url')
            self._filter(result, item)
        return result
        
        
    
    
    def list_content(self, page, url=None):
        result = []
        if not url: url = self.base_url
        data = util.substr(page, '<div class=\"contentArea', '<div class=\"pagination\">')
        pattern = '<h\d class=\"postTitle\"><a href=\"(?P<url>[^\"]+)(.+?)<span>(?P<title>[^<]+)</span></a></h\d>(.+?)<span class=\"postDate\">(?P<date>[^\<]+)</span>(.+?)<div class=\"postContent">[^<]+<a[^>]+[^<]+<img src=\"(?P<img>[^\"]+)(.+?)<div class=\"obs\">(?P<plot>.+?)</div>'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
            plot = re.sub('<br[^>]*>', '', m.group('plot'))
            item = self.video_item()
            item['title'] = m.group('title')
            item['img'] = m.group('img')
            item['plot'] = plot
            item['url'] = m.group('url')
            self._filter(result, item)
        data = util.substr(page, '<div class=\"pagination\">', '</div>')
        m = re.search('<li class=\"info\"><span>([^<]+)', data)
        n = re.search('<li class=\"prev\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)', data)
        k = re.search('<li class=\"next\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)', data)
        # replace last / + everyting till the end
        #myurl = re.sub('\/[\w\-]+$', '/', url)
        if not m == None:
            if not n == None:
                item = self.dir_item()
                item['type'] = 'prev'
                #item['title'] = '%s - %s' % (m.group(1), n.group('name'))
                item['url'] = n.group('url')
                result.append(item)
            if not k == None:
                item = self.dir_item()
                item['type'] = 'next'
                #item['title'] = '%s - %s' % (m.group(1), k.group('name'))
                item['url'] = k.group('url')
                result.append(item)
        return result


    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        resolved = []
        item = item.copy()
        url = self._url(item['url'])
        data = util.substr(util.request(url), '<div class=\"postContent\"', '</div>')
        playlist = re.search('playlistfile=(.+?\.xml)', data)
        if playlist:
            playlistxml = fromstring(util.request(playlist.group(1))).find('channel')
            jwplayer_ns = '{http://developer.longtailvideo.com/}'
            for item in playlistxml.findall('item'):
                title = item.find('title').text
                url = item.find(jwplayer_ns + 'file').text
                subs = item.find(jwplayer_ns + 'captions.file')
                subs = subs is not None and self._url(subs.text)
                res = resolver.findstreams(url, ['(?P<url>^.+?$)']) or []
                for i in res:
                    i['title'] = title
                    i['subs'] = subs
                resolved += res[:]
        else:
            resolved = resolver.findstreams(data, ['file=(?P<url>[^&]+)&amp'])
            subs = re.search('captions\.file=([^&]+)&amp', data)
            if resolved and subs:
                for i in resolved:
                    i['subs'] = subs.group(1)
                
        if not resolved:
            raise ResolveException('Video nenalezeno')
        for i in resolved:
            item = self.video_item()
            item['title'] = i['title']
            item['url'] = i['url']
            item['quality'] = i['quality']
            item['surl'] = i['surl']
            item['subs'] = i['subs']
            item['headers'] = i['headers']
            try:
                item['fmt'] = i['fmt']
            except KeyError:
                pass
            result.append(item)
        if len(result) > 0 and select_cb:
            return select_cb(result)
        return result
