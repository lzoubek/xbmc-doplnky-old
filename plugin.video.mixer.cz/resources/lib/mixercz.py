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
import random

import util
import jak
from provider import ContentProvider

CATEGORIES_START = '<div id="playlistsWrap">'
CATEGORIES_END = '</div>'
CATEGORIES_ITER_RE = '<li class=.*?> <(.+?)data-playlist-id=\"(?P<id>[^\"]+)\"(.+?)title=\"(?P<title>[^\"]+)\"(.+?)</li>'
HISTORIC_PLAYLIST_START = '<div id="historicPlaylists">'
HISTORIC_PLAYLIST_END = '<footer>'
HISTORIC_PLAYLIST_ITER_RE = '<li> <a href=\"http://www\.mixer\.cz/(?P<id>\d+)\"> <span class=\"date\">([^<]+)</span>(.+?)<span class=\"name\">(?P<title>[^<]+)<(.+?)</li>'

class MixerczContentProvider(ContentProvider):

    cptitle = u"{0} - {1}"
    iptitle = u"{0} ({1})"
    cpurl = u"{0}"
    plurl = u"#playlist#{0}#{1}"
    ipurl = u"#interpreter#{0}"
    vurl = u"http://cdn-dispatcher.stream.cz/?id={0}"
    imgurl = u"http://media.mixer.cz/thumb/large/{0}"

    def __init__(self, username=None, password=None, filter=None, tmp_dir='.'):
        ContentProvider.__init__(self, 'mixer.cz', 'http://www.mixer.cz/', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.paging = 50
        self.clips_path = os.path.join(tmp_dir, 'clips.json')


    def capabilities(self):
        return ['resolve', 'categories', 'search']


    def search(self, keyword):
        result = []
        data = jak.sendRPC('clip.search', keyword)
        for ip in data['interpreters']:
            item = self.dir_item()
            item['title'] = self.iptitle.format(ip['interpreter_name'], ip['interpreter_clips'])
            item['url'] = self.ipurl.format(ip['interpreter_id'])
            self._filter(result, item)
        for cp in data['clips']:
            item = self.video_item()
            ips = u", ".join([ip['name'] for ip in cp['interpreters']])
            item['title'] = self.cptitle.format(ips, cp['text'])
            item['url'] = self.cpurl.format(cp['clip_id'])
            item['menu'] = {}
            for ip in cp['interpreters']:
                item['menu'].update(self._create_interpreter_ctxitem(ip))
            self._filter(result, item)
        return result


    def categories(self):
        result = []
        if os.path.isfile(self.clips_path):
            os.remove(self.clips_path)
        data = util.substr(util.request(self.base_url), CATEGORIES_START, CATEGORIES_END)
        for m in re.finditer(CATEGORIES_ITER_RE, data, re.DOTALL):
            item = self.dir_item()
            item['title'] = m.group('title')
            item['url'] = self.plurl.format(m.group('id'), 0)
            item['menu'] = {u'Playlist':{'play':self.plurl.format(m.group('id'), 0), 'title':m.group('title'), 'action-type':'play'}}
            result.append(item)
        item = self.dir_item()
        item['title'] = u'Historie tématických playlistů'
        item['url'] = 'historie'
        result.append(item)
        return result


    def list(self, url):
        if url.startswith('#playlist#'):
            page = int(url.split("#")[-1])
            playlist_id = int(url.split("#")[-2])
            return self.list_playlist(playlist_id, page)
        elif url.startswith('#interpreter#'):
            return self.list_interpreter(int(url.split("#")[-1]))
        else:
            return self.list_historic_playlists(util.request(self._url(url)))

    def list_historic_playlists(self, page):
        result = []
        data = util.substr(page, HISTORIC_PLAYLIST_START, HISTORIC_PLAYLIST_END)
        for m in re.finditer(HISTORIC_PLAYLIST_ITER_RE, data, re.DOTALL):
            item = self.dir_item()
            item['title'] = m.group('title')
            item['url'] = self.plurl.format(m.group('id'), 0)
            item['menu'] = {u'Playlist':{'play':self.plurl.format(m.group('id'), 0), 'title':m.group('title'), 'action-type':'play'}}
            result.append(item)
        return result


    def list_playlist(self, playlist_id, page):
        result = []
        clips_id = self._get_clips_id(playlist_id)
        page_count = len(clips_id) / self.paging
        if page == page_count:
            clips_id = clips_id[self.paging * page:]
        else:
            clips_id = clips_id[self.paging * page:self.paging * page + self.paging]
        clips = self._get_clips_details(clips_id)
        for cp in clips:
            self._filter(result, self._create_clip_item(cp))
        if page > 0:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = self.plurl.format(playlist_id, page - 1)
            result.append(item)
        if page < page_count:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = self.plurl.format(playlist_id, page + 1)
            result.append(item)
        return result


    def list_interpreter(self, interpreter_id):
        result = []
        data = jak.sendRPC('playlist.getClipsByInterpreter', interpreter_id)
        clips_id = [clip['id'] for clip in data['clip']]
        clips = self._get_clips_details(clips_id)
        for cp in clips:
            self._filter(result, self._create_clip_item(cp))
        return result


    def _get_clips_id(self, playlist_id):
        try:
            with open(self.clips_path, 'r') as f:
                clips_id = util.json.loads(f.read())[str(playlist_id)]
        except IOError:
            data = jak.sendRPC('playlist.getClips', playlist_id)
            clips_id = [clip['id'] for clip in data['clip']]
            random.shuffle(clips_id)
            with open(self.clips_path, 'w') as f:
                dump = util.json.dumps({playlist_id:clips_id}, ensure_ascii=True)
                f.write(dump)
        except KeyError:
            data = jak.sendRPC('playlist.getClips', playlist_id)
            clips_id = [clip['id'] for clip in data['clip']]
            random.shuffle(clips_id)
            with open (self.clips_path, 'r+') as f:
                o = util.json.loads(f.read())
                o[playlist_id] = clips_id
                dump = util.json.dumps(o, ensure_ascii=True)
                f.seek(0)
                f.write(dump)
        return clips_id


    def _get_clips_details(self, clips_id):
        data = jak.sendRPC('playlist.getClipsDetail', clips_id)
        return data['clip']


    def _create_clip_item(self, clip):
        item = self.video_item()
        ips = u", ".join([ip['name'] for ip in clip['interpreters']])
        item['title'] = self.cptitle.format(ips, clip['title'])
        item['img'] = self.imgurl.format(clip['thumb'])
        item['url'] = self.cpurl.format((clip['id']))
        item['length'] = clip['length']
        item['menu'] = {}
        for ip in clip['interpreters']:
            item['menu'].update(self._create_interpreter_ctxitem(ip))
        return item


    def _create_interpreter_ctxitem(self, interpreter):
        name = self.iptitle.format(interpreter['name'], interpreter['clipCount'])
        namepl = name + u' playlist'
        params = self.ipurl.format((interpreter['id']))
        return  {name:{'list':params, 'action-type':'list'},
                     namepl:{'play':params, 'title':name, 'action-type':'play'}}


    def resolve(self, item, captcha_cb=None, select_cb=None):
        resolved = []
        item = item.copy()
        # interpreter playlist
        if item['url'].startswith("#interpreter#"):
            interpreter_id = int(item['url'].split('#')[-1])
            data = jak.sendRPC('playlist.getClipsByInterpreter', interpreter_id)
            clips_id = [clip['id'] for clip in data['clip']]
        # playlist
        elif item['url'].startswith('#playlist#'):
            playlist_id = int(item['url'].split('#')[-2])
            clips_id = self._get_clips_id(playlist_id)[:self.paging]
        else:
        # one video
            clips_id = [int(item['url'])]
        try:
            data = jak.sendRPC('playlist.getClipsDetail', clips_id)
        except Exception as e:
            self.error(str(e))
        else:
            for clip in data['clip']:
                for video in clip['cdn_qualities']:
                    item = self.video_item()
                    ips = u", ".join([ip['name'] for ip in clip['interpreters']])
                    item['title'] = self.cptitle.format(ips, clip['title'])
                    item['surl'] = unicode(clip['id'])
                    item['url'] = self.vurl.format(video['cdn_id'])
                    item['quality'] = video['quality']
                    resolved.append(item)
        resolved = sorted(resolved, key=lambda i:i['quality'])
        resolved = sorted(resolved, key=lambda i:len(i['quality']))
        resolved.reverse()
        if len(resolved) == 1:
            return resolved[0]
        return select_cb(resolved)
