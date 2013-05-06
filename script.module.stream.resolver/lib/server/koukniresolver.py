# -*- coding: UTF-8 -*-
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
import re,util,urllib2,traceback
__name__ = 'koukni.cz'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def url(url):
    m = _regex(url)
    if not m == None:
        iframe = _iframe(url)
        if iframe:
            return iframe[0]['url']
        else:
            return [url]
def resolve(url):
    m = _regex(url)
    if not m == None:
        try:
            iframe = _iframe(url)
        except:
            traceback.print_exc()
            return
        if iframe:
            return iframe
        else:
            return [{'name':__name__,'quality':'720p','url':url,'surl':url}]

def _furl(url):
    if url.startswith('http'):
        return url
    url = url.lstrip('./')
    return 'http://www.koukni.cz/'+url

def _iframe(url):
    iframe = re.search('(\d+)$',url,re.IGNORECASE | re.DOTALL)
    if iframe:
        data = util.request(url)
        video = re.search('<source type=\"video\/mp4\" src=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
        subs = re.search('<track src=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
        if video:
            ret = {'name':__name__,'quality':'720p','surl':url}
            ret['url'] = _furl(video.group('url'))
            if subs:
                ret['subs'] = _furl(subs.group('url'))
            return [ret]

def _regex(url):
    return re.search('(www\.)?koukni.cz/(.+?)',url,re.IGNORECASE | re.DOTALL)
