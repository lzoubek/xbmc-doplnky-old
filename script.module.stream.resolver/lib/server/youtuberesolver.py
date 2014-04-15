# -*- coding: UTF-8 -*-
'''
   YouTube plugin for XBMC
    Copyright (C) 2010-2012 Tobias Ussing And Henrik Mosgaard Jensen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import urllib
import cgi
import simplejson as json


class YoutubePlayer(object):
    fmt_value = {
            5: "240p",
            18: "360p",
            22: "720p",
            26: "???",
            33: "???",
            34: "360p",
            35: "480p",
            37: "1080p",
            38: "720p",
            43: "360p",
            44: "480p",
            45: "720p",
            46: "520p",
            59: "480",
            78: "400",
            82: "360p",
            83: "240p",
            84: "720p",
            85: "520p",
            100: "360p",
            101: "480p",
            102: "720p",
            120: "hd720",
            121: "hd1080"
            }

    # YouTube Playback Feeds
    urls = {}
    urls['video_stream'] = "http://www.youtube.com/watch?v=%s&safeSearch=none"
    urls['embed_stream'] = "http://www.youtube.com/get_video_info?video_id=%s"
    urls['video_info'] = "http://gdata.youtube.com/feeds/api/videos/%s"

    def __init__(self):
        pass

    def removeAdditionalEndingDelimiter(self, data):
        pos = data.find("};")
        if pos != -1:
            data = data[:pos + 1]
        return data

    def extractFlashVars(self, data, assets):
        flashvars = {}
        found = False

        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break
        data = self.removeAdditionalEndingDelimiter(data)

        if found:
            data = json.loads(data)
            if assets:
                flashvars = data["assets"]
            else:
                flashvars = data["args"]
        return flashvars

    def scrapeWebPageForVideoLinks(self, result, video):
        links = {}
        flashvars = self.extractFlashVars(result,0)
        if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
            return links

        if flashvars.has_key(u"ttsurl"):
            video[u"ttsurl"] = flashvars[u"ttsurl"]
        if flashvars.has_key("title"):
            video["title"] = flashvars["title"]

        for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
            url_desc_map = cgi.parse_qs(url_desc)
            if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
                continue

            key = int(url_desc_map[u"itag"][0])
            url = u""
            if url_desc_map.has_key(u"url"):
                url = urllib.unquote(url_desc_map[u"url"][0])
            elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
                url = urllib.unquote(url_desc_map[u"conn"][0])
                if url.rfind("/") < len(url) -1:
                    url = url + "/"
                url = url + urllib.unquote(url_desc_map[u"stream"][0])
            elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
                url = urllib.unquote(url_desc_map[u"stream"][0])

            if url_desc_map.has_key(u"sig"):
                url = url + u"&signature=" + url_desc_map[u"sig"][0]
            elif url_desc_map.has_key(u"s"):
                sig = url_desc_map[u"s"][0]
                flashvars = self.extractFlashVars(result, 1)
                js = flashvars[u"js"]
                url = url + u"&signature=" + self.decrypt_signature(sig)

            links[key] = url

        return links

    def decrypt_signature(self, s):
        ''' use decryption solution by Youtube-DL project '''
        if len(s) == 93:
            return s[86:29:-1] + s[88] + s[28:5:-1]
        elif len(s) == 92:
            return s[25] + s[3:25] + s[0] + s[26:42] + s[79] + s[43:79] + s[91] + s[80:83]
        elif len(s) == 91:
            return s[84:27:-1] + s[86] + s[26:5:-1]
        elif len(s) == 90:
            return s[25] + s[3:25] + s[2] + s[26:40] + s[77] + s[41:77] + s[89] + s[78:81]
        elif len(s) == 89:
            return s[84:78:-1] + s[87] + s[77:60:-1] + s[0] + s[59:3:-1]
        elif len(s) == 88:
            return s[7:28] + s[87] + s[29:45] + s[55] + s[46:55] + s[2] + s[56:87] + s[28]
        elif len(s) == 87:
            return s[6:27] + s[4] + s[28:39] + s[27] + s[40:59] + s[2] + s[60:]
        elif len(s) == 86:
            return s[5:34] + s[0] + s[35:38] + s[3] + s[39:45] + s[38] + s[46:53] + s[73] + s[54:73] + s[85] + s[74:85] + s[53]
        elif len(s) == 85:
            return s[3:11] + s[0] + s[12:55] + s[84] + s[56:84]
        elif len(s) == 84:
            return s[81:36:-1] + s[0] + s[35:2:-1]
        elif len(s) == 83:
            return s[81:64:-1] + s[82] + s[63:52:-1] + s[45] + s[51:45:-1] + s[1] + s[44:1:-1] + s[0]
        elif len(s) == 82:
            return s[80:73:-1] + s[81] + s[72:54:-1] + s[2] + s[53:43:-1] + s[0] + s[42:2:-1] + s[43] + s[1] + s[54]
        elif len(s) == 81:
            return s[56] + s[79:56:-1] + s[41] + s[55:41:-1] + s[80] + s[40:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]
        elif len(s) == 80:
            return s[1:19] + s[0] + s[20:68] + s[19] + s[69:80]
        elif len(s) == 79:
            return s[54] + s[77:54:-1] + s[39] + s[53:39:-1] + s[78] + s[38:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]

    def extractVideoLinksFromYoutube(self, url, videoid,video):
        result = util.request(self.urls[u"video_stream"] % videoid)
        links = self.scrapeWebPageForVideoLinks(result, video)
        if len(links) == 0:
            util.error(u"Couldn't find video url- or stream-map.")
        return links
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
import re,util,urllib
__name__ = 'youtube'


def supports(url):
    return not _regex(url) == None

def resolve(url):
    m = _regex(url)
    if not m == None:
        player = YoutubePlayer()
        video = {'title':'žádný název'}
        index = url.find('&') # strip out everytihing after &
        if index > 0:
            url = url[:index]
        links = player.extractVideoLinksFromYoutube(url,m.group('id'),video)
        resolved = []
        for q in links:
            if q in player.fmt_value.keys():
                quality = player.fmt_value[q]
                item = {}
                item['name'] = __name__
                item['url'] = links[q]
                item['quality'] = quality
                item['surl'] = url
                item['subs'] = ''
                item['title'] = video['title']
                item['fmt'] = q
                resolved.append(item)
        return resolved

def _regex(url):
    return re.search('www\.youtube\.com/(watch\?v=|v/|embed/)(?P<id>.+?)(\?|$|&)',url,re.IGNORECASE | re.DOTALL)

