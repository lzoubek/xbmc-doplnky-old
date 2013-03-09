# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 mx3L
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
import re, util
__name__ = 'videomail'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def resolve(url):
    m = _regex(url)
    if m:
        items = []
        headers = {
                   "Referer":"http://img.mail.ru/r/video2/uvpv3.swf?3",
                   "Cookie":"VID=2SlVa309oFH4; mrcu=EE18510E964723319742F901060A; p=IxQAAMr+IQAA; video_key=203516; s="
                  }
        # header "Cookie" with parameters need to be set for your download/playback
        quality = "???"
        data = util.request('http://api.video.mail.ru/videos/' + m.group('url') + '.json', headers=headers)
        item = util.json.loads(data)
        for qual in item[u'videos']:
            if qual == 'sd':
                quality = "480p"
            elif qual == "hd":
                quality = "720p"
            else:
                quality = "???"
            link = item[u'videos'][qual]
            items.append({'quality':quality, 'url':link, 'headers':headers})
        return items

def _regex(url):
    return re.search('http://img\.mail\.ru.*?<param.value=\"movieSrc=(?P<url>[^\"]+)', url, re.IGNORECASE | re.DOTALL)
