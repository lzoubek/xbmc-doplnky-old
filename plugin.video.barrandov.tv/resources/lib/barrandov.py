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
import cookielib
from threading import Lock

import util
from provider import ContentProvider

CATEGORIES_START = '<div id="right-menu">'
CATEGORIES_END = '<div class="block tip">'
CATEGORIES_ITER_RE = '<li.*?<a href=\"(?P<url>[^"]+)">(?P<title>.+?)</a><\/li>'
CATEGORY_IMG_RE = '<div class=\"header-container\">\s+<div class=\"content\">\s+<img src=\"(?P<img>[^\"]+)\"'
LISTING_START = '<div class="block video show-archive">'
LISTING_END = '<div id="right-menu">'
LISTING_ITER_RE = '<div class=\"item.*?\">.+?<a href=\"(?P<url>[^"]+)\">(?P<title>[^<]+)<.+?<p class=\"desc\">(?P<desc>[^<]+)</p>.+?<img src=\"(?P<img>[^\"]+)\".+?<span class=\"play\"><img src=\"(?P<playimg>[^\"]+)\".+?</div>'
PAGER_RE = '<span class=\"pages">(?P<actpage>[0-9]+)/(?P<totalpage>[0-9]+)</span>.*?<a href=\"(?P<nexturl>[^"]+)'
VIDEOLINK_ITER_RE = 'file:.*?\"(?P<url>[^"]+)".+?label:.*?\"(?P<quality>[^"]+)\"'
YELLOW_IMG = 'video-play-yellow'

class BarrandovContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'barrandov.tv', 'http://www.barrandov.tv', username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        
    def capabilities(self):
        return ['categories', 'resolve']

    def list(self, url):
        result = []
        if url.startswith('#top#'):
            url = 'video/vypis/nejsledovanejsi-videa/'
        elif url.startswith('#new#'):
            url = 'video/vypis/nejnovejsi-videa/'
            
        page = util.request(self._url(url))
        page = util.substr(page, LISTING_START, LISTING_END)
        for m in re.finditer(LISTING_ITER_RE, page, re.DOTALL | re.IGNORECASE):
            # skip payed content
            if m.group('playimg').find(YELLOW_IMG) != -1:
                continue
            date_m = re.search('(\d{1,2})\.(\d{1,2})\.(\d{4})', m.group('desc'))
            day = len(date_m.group(1)) > 1 and date_m.group(1)[0] == '0' and date_m.group(1)[1] or date_m.group(1)
            month = len(date_m.group(2)) > 1 and date_m.group(2)[0] == '0' and date_m.group(2)[1]  or date_m.group(2)
            year = date_m.group(3)
            date = '%s.%s.%s' % (day, month, year)
            title = "%s %s" % (m.group('title'), date) if m.group('title').find(date) == -1 else m.group('title')
            
            item = self.video_item()
            item['title'] = "%s %s" % (title, date) if title. find(date) == -1 else title
            item['url'] = self._url(m.group('url'))
            item['img'] = self._url(m.group('img'))
            self._filter(result, item)

        pager_m = re.search(PAGER_RE, page, re.DOTALL)
        if pager_m:
            item = self.dir_item()
            item['type'] = 'next'
            next_url = pager_m.group('nexturl')
            idx = url.find('?')
            if idx != -1:
                next_url = url[:idx] + next_url
            else:
                next_url = url + next_url
            item['url'] = next_url
            result.append(item)
        return result
    
        
    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = "#new#"
        result.append(item)
        item = self.dir_item()
        item['type'] = 'top'
        item['url'] = "#top#"
        result.append(item)
    
        categories = []
        page = util.request(self._url('/video'))
        page = util.substr(page, CATEGORIES_START, CATEGORIES_END)
        for item in re.finditer(CATEGORIES_ITER_RE, page, re.DOTALL | re.IGNORECASE):
            title = item.group('title')
            url = self._url(item.group('url'))
            categories.append((title, url))
        self._fill_categories_parallel(result, categories)
        sorted(result, key=lambda x:x['title'])
        return result
        
    def _fill_categories_parallel(self, list, categories):
        def process_category(title, url):
            page = util.request(url)
            img_m = re.search(CATEGORY_IMG_RE, page, re.IGNORECASE)
            img = img_m and self._url(img_m.group(1))
            page = util.substr(page, LISTING_START, LISTING_END)
            finditer = False
            for m in re.finditer(LISTING_ITER_RE, page, re.DOTALL | re.IGNORECASE):
                finditer = True
                # payed content
                if m.group('playimg').find(YELLOW_IMG) != -1:
                    return
                break
            # no links
            if not finditer:
                return
            item = self.dir_item()
            item['title'] = title
            item['url'] = url
            item['img'] = img
            with lock:
                self._filter(list, item)
        lock = Lock()
        util.run_parallel_in_threads(process_category, categories)


    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        item = item.copy()
        data = util.request(self._url(item['url']))
    
        for m in re.finditer(VIDEOLINK_ITER_RE, data, re.DOTALL | re.IGNORECASE):
            item = self.video_item()
            item['url' ]= self._url(m.group('url'))
            item['quality'] = m.group('quality')
            result.append(item)
        result.reverse()
        return select_cb(result)
