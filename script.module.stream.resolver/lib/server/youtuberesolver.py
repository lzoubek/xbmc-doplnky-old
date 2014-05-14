# -*- coding: UTF-8 -*-

import urllib2
# source from https://github.com/rg3/youtube-dl/issues/1208
# removed some unnecessary debug messages..
class CVevoSignAlgoExtractor:
    # MAX RECURSION Depth for security
    MAX_REC_DEPTH = 5

    def __init__(self):
        self.algoCache = {}
        self._cleanTmpVariables()

    def _cleanTmpVariables(self):
        self.fullAlgoCode = ''
        self.allLocalFunNamesTab = []
        self.playerData = ''

    def _jsToPy(self, jsFunBody):
        pythonFunBody = jsFunBody.replace('function', 'def').replace('{', ':\n\t').replace('}', '').replace(';', '\n\t').replace('var ', '')
        pythonFunBody = pythonFunBody.replace('.reverse()', '[::-1]')

        lines = pythonFunBody.split('\n')
        for i in range(len(lines)):
            # a.split("") -> list(a)
            match = re.search('(\w+?)\.split\(""\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), 'list(' + match.group(1) + ')')
            # a.length -> len(a)
            match = re.search('(\w+?)\.length', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), 'len(' + match.group(1) + ')')
            # a.slice(3) -> a[3:]
            match = re.search('(\w+?)\.slice\(([0-9]+?)\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), match.group(1) + ('[%s:]' % match.group(2)))
            # a.join("") -> "".join(a)
            match = re.search('(\w+?)\.join\(("[^"]*?")\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), match.group(2) + '.join(' + match.group(1) + ')')
        return "\n".join(lines)

    def _getLocalFunBody(self, funName):
        # get function body
        match = re.search('(function %s\([^)]+?\){[^}]+?})' % funName, self.playerData)
        if match:
            # return jsFunBody
            return match.group(1)
        return ''

    def _getAllLocalSubFunNames(self, mainFunBody):
        match = re.compile('[ =(,](\w+?)\([^)]*?\)').findall(mainFunBody)
        if len(match):
            # first item is name of main function, so omit it
            funNameTab = set(match[1:])
            return funNameTab
        return set()

    def decryptSignature(self, s, playerUrl):
        playerUrl = playerUrl[:4] != 'http' and 'http:' + playerUrl or playerUrl
        util.debug("decrypt_signature sign_len[%d] playerUrl[%s]" % (len(s), playerUrl))

        # clear local data
        self._cleanTmpVariables()

        # use algoCache
        if playerUrl not in self.algoCache:
            # get player HTML 5 sript
            request = urllib2.Request(playerUrl)
            try:
                self.playerData = urllib2.urlopen(request).read()
                self.playerData = self.playerData.decode('utf-8', 'ignore')
            except:
                util.debug('Unable to download playerUrl webpage')
                return ''

            # get main function name
            match = re.search("signature=(\w+?)\([^)]\)", self.playerData)
            if match:
                mainFunName = match.group(1)
                util.debug('Main signature function name = "%s"' % mainFunName)
            else:
                util.debug('Can not get main signature function name')
                return ''

            self._getfullAlgoCode(mainFunName)

            # wrap all local algo function into one function extractedSignatureAlgo()
            algoLines = self.fullAlgoCode.split('\n')
            for i in range(len(algoLines)):
                algoLines[i] = '\t' + algoLines[i]
            self.fullAlgoCode = 'def extractedSignatureAlgo(param):'
            self.fullAlgoCode += '\n'.join(algoLines)
            self.fullAlgoCode += '\n\treturn %s(param)' % mainFunName
            self.fullAlgoCode += '\noutSignature = extractedSignatureAlgo( inSignature )\n'

            # after this function we should have all needed code in self.fullAlgoCode
            try:
                algoCodeObj = compile(self.fullAlgoCode, '', 'exec')
            except:
                util.debug('decryptSignature compile algo code EXCEPTION')
                return ''
        else:
            # get algoCodeObj from algoCache
            util.debug('Algo taken from cache')
            algoCodeObj = self.algoCache[playerUrl]

        # for security alow only flew python global function in algo code
        vGlobals = {"__builtins__": None, 'len': len, 'list': list}

        # local variable to pass encrypted sign and get decrypted sign
        vLocals = { 'inSignature': s, 'outSignature': '' }

        # execute prepared code
        try:
            exec(algoCodeObj, vGlobals, vLocals)
        except:
            util.debug('decryptSignature exec code EXCEPTION')
            return ''

        util.debug('Decrypted signature = [%s]' % vLocals['outSignature'])
        # if algo seems ok and not in cache, add it to cache
        if playerUrl not in self.algoCache and '' != vLocals['outSignature']:
            util.debug('Algo from player [%s] added to cache' % playerUrl)
            self.algoCache[playerUrl] = algoCodeObj

        # free not needed data
        self._cleanTmpVariables()

        return vLocals['outSignature']

    # Note, this method is using a recursion
    def _getfullAlgoCode(self, mainFunName, recDepth=0):
        if self.MAX_REC_DEPTH <= recDepth:
            util.debug('_getfullAlgoCode: Maximum recursion depth exceeded')
            return

        funBody = self._getLocalFunBody(mainFunName)
        if '' != funBody:
            funNames = self._getAllLocalSubFunNames(funBody)
            if len(funNames):
                for funName in funNames:
                    if funName not in self.allLocalFunNamesTab:
                        self.allLocalFunNamesTab.append(funName)
                        util.debug("Add local function %s to known functions" % mainFunName)
                        self._getfullAlgoCode(funName, recDepth + 1)

            # conver code from javascript to python
            funBody = self._jsToPy(funBody)
            self.fullAlgoCode += '\n' + funBody + '\n'
        return

decryptor = CVevoSignAlgoExtractor()

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
        flashvars = self.extractFlashVars(result, 0)
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
                if url.rfind("/") < len(url) - 1:
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
                url = url + u"&signature=" + self.decrypt_signature(sig, js)

            links[key] = url

        return links

    def decrypt_signature(self, s, js):
        return decryptor.decryptSignature(s, js)


    def extractVideoLinksFromYoutube(self, url, videoid, video):
        result = util.request(self.urls[u"video_stream"] % videoid)
        links = self.scrapeWebPageForVideoLinks(result, video)
        if len(links) == 0:
            util.error(u"Couldn't find video url- or stream-map.")
        return links
# /*
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
import re, util, urllib
__name__ = 'youtube'


def supports(url):
    return not _regex(url) == None

def resolve(url):
    m = _regex(url)
    if not m == None:
        player = YoutubePlayer()
        video = {'title':'žádný název'}
        index = url.find('&')  # strip out everytihing after &
        if index > 0:
            url = url[:index]
        links = player.extractVideoLinksFromYoutube(url, m.group('id'), video)
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
    return re.search('www\.youtube\.com/(watch\?v=|v/|embed/)(?P<id>.+?)(\?|$|&)', url, re.IGNORECASE | re.DOTALL)
