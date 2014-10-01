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
import random
from urlparse import urlparse
from xml.etree.ElementTree import fromstring

import util
from provider import ContentProvider

VYSIELANE_START = '<div class="archiveList preloader">'
VYSIELANE_ITER_RE = '<ul class=\"clearfix\">.*?<div class=\"titleBg">.*?<a href=\"(?P<url>[^"]+).*?title=\"(?P<title>[^"]+).+?<p>(?P<desc>.*?)</p>.+?</ul>'
NEVYSIELANE_START = '<div class="archiveNev">'
NEVYSIELANE_END = '<div class="clearfix padSection">'
NEVYSIELANE_ITER_RE = '<li.*?><a href=\"(?P<url>[^"]+).*?title=\"(?P<title>[^"]+).*?</li>'
EPISODE_START = '<div class="episodeListing relative overflowed">'
EPISODE_END = '<div class="centered pagerDots"></div>'
EPISODE_ITER_RE = '<li[^>]*>\s+?<a href=\"(?P<url>[^"]+)\" title=\"(?P<title>[^"]+)\">\s+?<span class=\"date\">(?P<date>[^<]+)</span>(.+?)<span class=\"episode\">(?P<episode>[^0]{1}[0-9]*)</span>(.+?)</li>'
SERIES_START = EPISODE_START
SERIES_END = EPISODE_END
SERIES_ITER_RE = '<option(.+?)data-ajax=\"(?P<url>[^\"]+)\">(?P<title>[^<]+)</option>'
TOP_GENERAL_START = '<span class="subtitle">výber toho najlepšieho</span>'
TOP_GENERAL_END = '</div>'
TOP_GENERAL_ITER_RE = '<li>\s+?<a href=\"(?P<url>[^"]+)\" title=\"(?P<title>[^"]+)\">(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)</li>'
NEWEST_STATION_START = '<span class="subtitle">najnovšie videá</span>'
NEWEST_STATION_END = '<ul class="listing preloader">'
NEWEST_STATION_ITER_RE = '<option(.+?)value=\"(?P<station>[^\"]+)\"(.+?)data-ajax=\"(?P<url>[^\"]+)\">(.+?)<\/option>'
NEWEST_ITER_RE = '<li><a href=\"(?P<url>[^\"]+)\" title=\"(?P<title>[^\"]+)\"><span class=\"time\">(?P<time>[^<]+)</span>(.+?)</li>'
JOJ_FILES_ITER_RE = '<file type=".+?" quality="(?P<quality>.+?)" id="(?P<id>.+?)" label=".+?" path="(?P<path>.+?)"/>'

MAX_PAGE_ENTRIES = 100

JOJ_URL = 'http://www.joj.sk'
JOJ_PLUS_URL = 'http://plus.joj.sk'
WAU_URL = 'http://wau.joj.sk/'
SENZI_URL = 'http://senzi.joj.sk/'

RELACIE_FIX = ['anosefe']
SERIALY_FIX = []
VYMENIT_LINK = {'csmatalent':'http://www.csmatalent.cz/video-cz.html'}
CHANGE_PATH = { 'www': 'joj', 'plus': 'jojplus' }

def fix_link(url):
    if url in SERIALY_FIX:
        url = url[:url.rfind('-')] + '-epizody.html'
    elif url in RELACIE_FIX:
        url = url[:url.rfind('-')] + '-archiv.html'
    else:
        for rel in VYMENIT_LINK.keys():
            if rel in url:
                return VYMENIT_LINK[rel]
    return url

def fix_path(path):
    for rel in CHANGE_PATH.keys():
        if rel in path:
            return CHANGE_PATH[rel]
    return path

class JojContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None):
        ContentProvider.__init__(self, 'joj.sk', 'http://www.joj.sk/', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories', 'resolve', '!download']

    def list(self, url):
        if url.find('#cat#') == 0:
            url = url[5:]
            return self.subcategories(url)
        if url.find('#top#') == 0:
            return self.list_top()
        if url.find('#subcat#') == 0:
            url = url[8:]
            return self.list_show(url)
        if url.find('#series#') == 0:
            url = url[8:]
            result = self.list_series(url)
            if not result:
                result = self.list_episodes(url)
            return result
        if url.find('#episodes#') == 0:
            page = int(re.search('^#episodes##([^#]+)', url).group(1))
            url = re.search('^#episodes##[^#]+#([^$]+)', url).group(1)
            return self.list_episodes(url, page)
        if url.find('#new#') == 0:
            return self.list_new()

    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = "#new#"
        result.append(item)
        item = self.dir_item()
        item['type'] = 'top'
        item['url'] = '#top#' + JOJ_URL
        result.append(item)
        item = self.dir_item()
        item['title'] = 'JOJ'
        item['img'] = None  # logo..
        item['url'] = "#cat#" + JOJ_URL + '/archiv.html'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'JOJ Plus'
        item['url'] = "#cat#" + JOJ_PLUS_URL + '/plus-archiv.html'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'WAU'
        item['url'] = "#cat#" + WAU_URL + '/wau-archiv.html'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Senzi'
        item['url'] = "#cat#" + SENZI_URL + '/senzi-archiv.html'
        result.append(item)
        return result

    def subcategories(self, url):
        result = []
        if url.startswith(('#rel#','#ser#')):
            url = url[5:]
            item = self.dir_item()
            item['title'] = 'Vysielane'
            item['url'] = '#subcat##showon#' + url
            result.append(item)
            item = self.dir_item()
            item['title'] = 'Nevysielane'
            item['url'] = '#subcat##showoff#' + url
            self._filter(result, item)
        else:
            item = self.dir_item()
            item['title'] = 'Relacie'
            item['url'] = "#cat##rel#" + url + '/?type=relacie'
            self._filter(result, item)
            item = self.dir_item()
            item['title'] = 'Serialy'
            item['url'] = "#cat##ser#" + url + '/?type=serialy'
            self._filter(result, item)
            item = self.video_item()
            item['title'] = 'Live'
            item['url'] = url.replace('archiv', 'live')
            self._filter(result, item)
        return result

    def list_show(self, url):
        result = []
        prefix = "#series#"
        if url.startswith("#showon#"):
            page = util.request(url[8:])
            page = util.substr(page, VYSIELANE_START, NEVYSIELANE_START)
            for m in re.finditer(VYSIELANE_ITER_RE, page, re.DOTALL | re.IGNORECASE):
                item = self.dir_item()
                item['title'] = m.group('title')
                item['plot'] = m.group('desc')
                item['url'] = prefix + m.group('url')
                self._filter(result, item)

        elif url.startswith("#showoff#"):
            page = util.request(url[9:])
            page = util.substr(page, NEVYSIELANE_START, NEVYSIELANE_END)
            for m in re.finditer(NEVYSIELANE_ITER_RE, page, re.DOTALL | re.IGNORECASE):
                item = self.dir_item()
                item['title'] = m.group('title')
                item['url'] = prefix + m.group('url')
                self._filter(result, item)
        result.sort(key=lambda x:x['title'].lower())
        return result

    def list_series(self, url):
        result = []
        page = util.request(url)
        page = util.substr(page, SERIES_START, SERIES_END)
        for m in re.finditer(SERIES_ITER_RE, page, re.DOTALL | re.IGNORECASE):
            item = self.dir_item()
            item['title'] = m.group('title')
            item['url'] = "#episodes##0#" + 'http://' + urlparse(url).netloc + '/ajax.json?' + m.group('url')
            self._filter(result, item)
        return result

    def list_episodes(self, url, page=0):
        result = []
        if url.find('ajax.json') != -1:
            headers = {'X-Requested-With':'XMLHttpRequest',
                       'Referer':util.substr(url, url, url.split('/')[-1])
                       }
            httpdata = util.request(url, headers)
            httpdata = util.json.loads(httpdata)['content']
        else:
            httpdata = util.request(url)
            httpdata = util.substr(httpdata, EPISODE_START, EPISODE_END)

        entries = 0
        skip_entries = MAX_PAGE_ENTRIES * page

        for m in re.finditer(EPISODE_ITER_RE, httpdata, re.DOTALL | re.IGNORECASE):
            entries += 1
            if entries < skip_entries:
                continue
            item = self.video_item()
            item['title'] = "%s. %s (%s)" % (m.group('episode'), m.group('title'), m.group('date'))
            item['url'] = m.group('url')
            self._filter(result, item)
            if entries >= (skip_entries + MAX_PAGE_ENTRIES):
                page += 1
                item = self.dir_item()
                item['type'] = 'next'
                item['url'] = "#episodes##%d#" % (page) + url
                self._filter(result, item)
                break
        return result

    def list_top(self):
        result = []
        page = util.request(self.base_url)
        page = util.substr(page, TOP_GENERAL_START, TOP_GENERAL_END)
        for m in re.finditer(TOP_GENERAL_ITER_RE, page, re.DOTALL | re.IGNORECASE):
            item = self.video_item()
            item['title'] = m.group('title')
            item['url'] = m.group('url')
            item['img'] = m.group('img')
            self._filter(result, item)
        return result

    def list_new(self):
        result = []
        page = util.request(self.base_url)
        page = util.substr(page, NEWEST_STATION_START, NEWEST_STATION_END)
        for m_s in re.finditer(NEWEST_STATION_ITER_RE, page, re.DOTALL | re.IGNORECASE):
            url = 'http://' + urlparse(self.base_url).netloc + '/ajax.json?' + m_s.group('url')
            headers = {'X-Requested-With':'XMLHttpRequest',
                       'Referer':self.base_url
                       }
            httpdata = util.request(url, headers)
            httpdata = util.json.loads(httpdata)['content']
            for m_v in re.finditer(NEWEST_ITER_RE, httpdata, re.DOTALL):
                item = self.video_item()
                item['title'] = "[%s] %s (%s)" % (m_s.group('station'), m_v.group('title'), m_v.group('time'))
                item['url'] = m_v.group('url')
                self._filter(result, item)
        return result

    def rtmp_url(self, playpath, pageurl, type=None, balance=None):
        if balance is not None and type is not None:
            try:
                nodes = balance.find('project[@id="joj"]').find('balance[@type="%s"]'%(type))
                min_node = int(nodes.find('node').attrib.get('id'))
                max_node = int(nodes.findall('node')[-1].attrib.get('id'))
                node_id = random.randint(min_node, max_node)
                server = balance.find('nodes').find('node[@id="%d"]'%node_id).attrib.get('url')
            except Exception as e:
                self.error("cannot get stream server: %s"%(str(e)))
                self.info("using default stream server")
                server = 'n11.joj.sk'
        else:
            server = 'n11.joj.sk'
        swfurl = 'http://player.joj.sk/JojPlayer.swf?no_cache=137034'
        return 'rtmp://' + server + ' playpath=' + playpath + ' pageUrl=' + pageurl + ' swfUrl=' + swfurl + ' swfVfy=true'

    # modified source from dmd-czech joj video plugin
    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        item = item.copy()
        url = item['url']
        if url.endswith('live.html'):
            for quality in ['360','540','720']:
                item = self.video_item()
                item['quality'] = quality + 'p'
                item['url'] = self.rtmp_url(fix_path(re.search('http://(\w+).joj.sk', url).group(1)) + '-' + quality, url)
                result.append(item)
        else:
            data = util.request(url)
            playerdata = re.search(r'<div\ class=\"jn-player\"(.+?)>',data).group(1)
            pageid = re.search(r'data-pageid=[\'\"]([^\'\"]+)',playerdata).group(1) 
            basepath = re.search(r'data-basepath=[\'\"]([^\'\"]+)',playerdata).group(1)
	    videoid = re.search(r'data-id=[\'\"]([^\'\"]+)',playerdata).group(1)
            playlisturl = basepath + 'services/Video.php?clip=' + videoid + 'pageId=' + pageid
            playlist = fromstring(util.request(playlisturl))
            balanceurl = basepath + 'balance.xml?nc=%d' % random.randint(1000, 9999)
            balance = fromstring(util.request(balanceurl))
            for video in playlist.find('files').findall('file'):
                item = self.video_item()
                item['img'] = playlist.attrib.get('large_image')
                item['length'] = playlist.attrib.get('duration')
                item['quality'] = video.attrib.get('quality')
                item['url'] = self.rtmp_url(video.attrib.get('path'), playlist.attrib.get('url'), video.attrib.get('type'), balance)
                result.append(item)
        result.reverse()
        return select_cb(result)
