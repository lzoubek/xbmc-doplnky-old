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
import traceback
import cookielib
import md5
from time import sleep

import util
from provider import ContentProvider

START_TOP = '<h2 class="nadpis">Najsledovanejšie</h2>'
END_TOP = '<h2 class="nadpis">Najnovšie</h2>'
TOP_ITER_RE = '<li(.+?)<a title=\"(?P<title>[^"]+)\"(.+?)href=\"(?P<url>[^"]+)\"(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)<p class=\"day\">(?P<date>[^<]+)<\/p>(.+?)<span class=\"programmeTime\">(?P<time>[^<]+)(.+?)<\/li>'

START_NEWEST = END_TOP
END_NEWEST = '<div class="footer'
NEWEST_ITER_RE = '<li(.+?)<a href=\"(?P<url>[^"]+)\"(.+?)title=\"(?P<title>[^"]+)\"(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)<p class=\"day\">(?P<date>[^<]+)<\/p>(.+?)<span class=\"programmeTime\">(?P<time>[^<]+)(.+?)<\/li>'

START_AZ = '<h2 class="az"'
END_AZ = START_TOP
AZ_ITER_RE = TOP_ITER_RE

START_LISTING = '<div class="boxRight archiv">'
END_LISTING = '<div class="boxRight soloBtn white">'
LISTING_PAGER_RE = "<a class=\'prev calendarRoller' href=\'(?P<prevurl>[^\']+)\'.+?<a class=\'next calendarRoller\' href=\'(?P<nexturl>[^\']+)"
LISTING_DATE_RE = "<div class=\'calendar-header\'>\s+<h6>(?P<date>.+?)</h6>"
LISTING_ITER_RE = '<td class=(\"day\"|\"active day\")>\s+<a href="(?P<url>[^\"]+)\">(?P<daynum>[\d]+)</a>\s+</td>'

EPISODE_START = '<div class="span9">'
EPISODE_END = '<div class="footer'
EPISODE_RE = '<div class=\"article-header\">\s+?<h2>(?P<title>[^<]+)</h2>(.+?)<div class=\"span6">\s+?<div[^>]+?>(?P<plot>[^<]+)</div>'

VIDEO_ID_RE = 'LiveboxPlayer.flash\(.+?stream_id:+.\"(.+?)\"'

class RtvsContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'rtvs.sk', 'http://www.rtvs.sk', username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.archive_url = self._url('tv.archive.alphabet/')
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def capabilities(self):
        return ['categories', 'resolve', '!download']

    def list(self, url):
        if url.find('#az#') == 0:
            return self.az()
        elif url.find('#new#') == 0:
            return self.list_new(util.request(self.archive_url))
        elif url.find('#top#') == 0:
            return self.list_top(util.request(self.archive_url))
        elif url.find('#listaz#') == 0:
            url = url[8:]
            return self.list_az(util.request(self.archive_url + url))
        else:
            return self.list_episodes(util.request(self._url(url)))
    
        
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
        item = self.dir_item()
        item['title'] = 'A-Z'
        item['url'] = "#az#"
        result.append(item)
        return result


    def az(self):
        result = []
        prefix = '#listaz#'
        item = self.dir_item()
        item['title'] = '0-9'
        item['url'] = prefix + '?letter=0-9'
        self._filter(result, item)
        for c in xrange(65, 90, 1):
            chr = str(unichr(c))
            item = self.dir_item()
            item['title'] = chr
            item['url'] = prefix + '?letter=%s' % chr.lower()
            self._filter(result, item)
        return result    


    def list_az(self, page):
        result = []
        images = []
        page = util.substr(page, START_AZ, END_AZ)
        for m in re.finditer(AZ_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            img = {'remote':self._url(m.group('img')),
                   'local' :self._get_image_path(self._url(m.group('img')))}
            item = self.dir_item()
            semicolon = m.group('title').find(':')
            if semicolon != -1:
                item['title'] = m.group('title')[:semicolon].strip()
            else:
                item['title'] = m.group('title')
            item['img'] = img['local']
            item['url'] = m.group('url')
            self._filter(result, item)
            images.append(img)
        self._get_images(images)
        return result


    def list_top(self, page):
        result = []
        images = []
        page = util.substr(page, START_TOP, END_TOP)
        for m in re.finditer(TOP_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            img = {'remote':self._url(m.group('img')),
                   'local' :self._get_image_path(self._url(m.group('img')))}
            item = self.video_item()
            item['title'] = "%s (%s - %s)" % (m.group('title'), m.group('date'), m.group('time'))
            item['img'] = img['local']
            item['url'] = m.group('url')
            self._filter(result, item)
            images.append(img)
        self._get_images(images)
        return result

        
    def list_new(self, page):
        result = []
        images = []
        page = util.substr(page, START_NEWEST, END_NEWEST)
        for m in re.finditer(NEWEST_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            img = {'remote':self._url(m.group('img')),
                   'local' :self._get_image_path(self._url(m.group('img')))}
            item = self.video_item()
            item['title'] = "%s (%s - %s)" % (m.group('title'), m.group('date'), m.group('time'))
            item['img'] = img['local']
            item['url'] = m.group('url')
            self._filter(result, item)
            images.append(img)
        self._get_images(images)
        return result
    
        
    def list_episodes(self, page):
        result = []
        episodes = []
        episode_page = page
        page = util.substr(page, START_LISTING, END_LISTING)
        current_date = re.search(LISTING_DATE_RE, page, re.IGNORECASE).group('date')
        prev_url = re.search(LISTING_PAGER_RE, page, re.IGNORECASE | re.DOTALL).group('prevurl')
        prev_url = re.sub('&amp;', '&', prev_url)
        for m in re.finditer(LISTING_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            episodes.append([self._url(re.sub('&amp;', '&', m.group('url'))), m])
        res = self._request_parallel(episodes)
        for p, m in res:
            m = m[0]
            item = self.list_episode(p)
            item['title'] = "%s (%s. %s)" % (item['title'], m.group('daynum'), current_date)
            item['date'] = m.group('daynum')
            item['url'] = re.sub('&amp;', '&', m.group('url'))
            self._filter(result, item)
        result.sort(key=lambda x:int(x['date']), reverse=True)

        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = prev_url
        self._filter(result, item)
        return result
    
    def list_episode(self, page):
        item = self.video_item()
        episode = re.search(EPISODE_RE, page, re.DOTALL)
        if episode:
            item['title'] = episode.group('title')
            item['plot'] = episode.group('plot')
        return item
        

    def resolve(self, item, captcha_cb=None, select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(url)
        video_id = re.search(VIDEO_ID_RE, data, re.IGNORECASE | re.DOTALL).group(1)
        headers = {'Referer':url}
        keydata = util.request("http://embed.stv.livebox.sk/v1/tv-arch.js", headers)
        rtmp_url_regex = "'(rtmp:\/\/[^']+)'\+videoID\+'([^']+)'"
        m3u8_url_regex = "'(http:\/\/[^']+)'\+videoID\+'([^']+)'"
        rtmp = re.search(rtmp_url_regex, keydata, re.DOTALL)
        m3u8 = re.search(m3u8_url_regex, keydata, re.DOTALL)
        m3u8_url = m3u8.group(1) + video_id + m3u8.group(2)
    
        # rtmp[t][e|s]://hostname[:port][/app[/playpath]]
        # tcUrl=url URL of the target stream. Defaults to rtmp[t][e|s]://host[:port]/app. 
        
        # rtmp url- fix podla mponline2 projektu
        rtmp_url = rtmp.group(1) + video_id + rtmp.group(2)
        stream_part = 'mp4:' + video_id
        playpath = rtmp_url[rtmp_url.find(stream_part):]
        tcUrl = rtmp_url[:rtmp_url.find(stream_part) - 1] + rtmp_url[rtmp_url.find(stream_part) + len(stream_part):]
        app = tcUrl[tcUrl.find('/', tcUrl.find('/') + 2) + 1:]
    
        # rtmp_url = rtmp_url+ ' playpath=' + playpath + ' tcUrl=' + tcUrl + ' app=' + app
        rtmp_url = rtmp_url + ' tcUrl=' + tcUrl + ' app=' + app
        item['url'] = rtmp_url
        return item
    
    def _request_parallel(self, requests):
        def fetch(req, *args):
            return util.request(req), args
        pages = []
        q = util.run_parallel_in_threads(fetch, requests)
        while True:
            try:
                page, args = q.get_nowait()
            except:
                break
            pages.append([page, args])
        return pages
            
    
    def _get_image_path(self, name):
        local = self.tmp_dir
        m = md5.new()
        m.update(name)
        image = os.path.join(local, m.hexdigest() + '_img.png')
        return image
       
    def _get_images(self, images):
        def download(remote, local):
            util.save_data_to_file(util.request(remote), local)
        not_cached = [(img['remote'], img['local'])
                       for img in images if not os.path.exists(img['local'])]
        util.run_parallel_in_threads(download, not_cached)
