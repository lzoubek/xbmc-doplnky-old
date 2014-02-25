# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2013 Maros Ondrasek
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
import os
import urllib2
import shutil
import cookielib
from urlparse import urlparse


import util, resolver
from provider import ContentProvider, ResolveException

CATEGORIES_START='Videa ONLINE'
CATEGORIES_END = '<li id="menu-item-1930"'
LISTING_START ='<div id="main" class="clear">'
LISTING_END = '<div id="main-bottom"></div>>'
LISTING_ITER_RE= '<div id=[^<]+<div class=\"date">[^<]+<div class=\"day">(?P<day>[^<]+)</div>\s+<div class=\"month\">(?P<month>[^<]+)</div>(.+?)<h2 class=\"title\"><a href=\"(?P<url>[^\"]+)\"[^>]+>(?P<title>[^<]+)</a></h2>(.+?)<p>(<img class(.+?)src=\"(?P<img>[^\"]+)\"[^\>]+>)?(?P<plot>.+?)<a class'
MENU_LISTING_ITER_RE= '<li id=\"(?P<id>[^\"]+)[^<]+<a href=\"(?P<url>[^\"]+)\">(?P<title>[^<]+)</a>\s+<ul class=\"sub-menu">'

PAGER_START = "<div class=\'wp-pagenavi\'>"
PAGER_END = "</div>"
PAGER_NEXT_RE = "<a href=\'(?P<url>[^\']+)\' class=\'nextpostslink\'>[^<]+</a>"
PAGER_PREV_RE = "<a href=\'(?P<url>[^\']+)\' class=\'previouspostslink\'>[^<]+</a>"


class GordonUraContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None):
        ContentProvider.__init__(self, 'gordon.ura.cz', 'http://gordon.ura.cz/', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories', 'resolve']

    def list(self, url):
        if url.startswith('#new#'):
            return self.list_page(util.request(self._url('?tag=online')))
        else:
            return self.list_page(util.request(self._url(url)))

    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = "#new#"
        result.append(item)

        for title, url in [('Kitchen Nightmares','?tag=KN-online'),
         ("Ramsay's Kitchen Nightmares","?tag=rkn-online"),
         ("Gordon's Great Escape","?tag=GGE-online"),
         ("Cookalong Live",'?cat=19'),
         ("MasterChef",'?tag=mc-online'),
         ("MasterChef Junior",'?tag=mcj-online'),
         ("Hell's Kitchen",'?tag=HK-online'),
         ("Hotel Hell",'?tag=HH-online'),
         ("Ramsey's Best Restaurant",'?cat=35'),
         ('The F Word','?tag=TFW-online'),
         ('Ostatní videa','?tag=ostatni-online')]:
            item = self.dir_item()
            item['title'] = title
            item['url'] = url
            result.append(item)
        return result

    def list_page(self, page):
        result = []
        page = util.substr(page, LISTING_START, LISTING_END)
        for m in re.finditer(LISTING_ITER_RE, page, re.DOTALL):
            item = self.video_item()
            item['title'] = '%s (%s %s)'%(m.group('title'), m.group('day'),m.group('month'))
            item['url'] = self._url(m.group('url'))
            item['img'] = m.group('img') and self._url(m.group('img')) or ''
            item['plot'] = m.group('plot')
            self._filter(result,item)
        page = util.substr(page, PAGER_START, PAGER_END)
        next_m = re.search(PAGER_NEXT_RE,page,re.DOTALL)
        prev_m = re.search(PAGER_PREV_RE,page,re.DOTALL)
        if prev_m:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = prev_m.group('url')
            result.append(item)
        if next_m:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = next_m.group('url')
            result.append(item)
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        item = item.copy()
        url = self._url(item['url'])
        data = util.substr(util.request(url), '<embed id', '>')
        yurl_m = re.search('file=.*?(http[^&]+)&',data,re.DOTALL)
        yurl = yurl_m and re.sub('youtu.be/','www.youtube.com/watch?v=',yurl_m.group(1)) or ''
        resolved = resolver.findstreams(yurl, ['(?P<url>[^&]+)'])
        subs = re.search('captions\.file=([^&]+)', data, re.DOTALL)
        if resolved and subs:
            for i in resolved:
                i['subs'] = self._url(subs.group(1))
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
            print item
            result.append(item)
        if len(result)  == 0:
            return result[0]
        return select_cb(result)
