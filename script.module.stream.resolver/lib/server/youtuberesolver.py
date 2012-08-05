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
import re,util,urllib
__name__ = 'youtube'
__eurl__ = ''
fmt_value = {
        '5': '240p',
	'17': '???',  # ???
        '18': '360p',
        '22': '720p',
        '26': '???',
        '33': '???',
        '34': '360p',
        '35': '480p',
	'36': '240p',
        '37': '1080p',
        '38': '720p',
        '43': '360p',
        '44': '480p',
        '45': '720p',
        '46': '520p',
        '59': '480p',
        '78': '400p',
        '82': '360p',
        '83': '240p',
        '84': '720p',
        '85': '520p',
        '100': '360p',
        '101': '480p',
        '102': '720p'
        }


def supports(url):
	return not _regex(url) == None

def resolve(url):
	m = _regex(url)
	if not m == None:
		request = urllib.urlencode({'video_id':m.group('id'),'el':'embedded','asv':'3','hl':'en_US','eurl':__eurl__})
		data = util.request('http://www.youtube.com/get_video_info?%s' % request)
		data = urllib.unquote(util.decode_html(data))
		
		if data.find('status=fail') > -1:
			util.error('youtube resolver failed: '+data+' videoid:'+m.group('id'))
		else:
			# to avoid returning more than 1 url of same quality
			qualities = []
			resolved = []
			for n in re.finditer('(=|,|\|)url=(?P<url>.+?)(,|\||fallback_host).+?itag=(?P<q>\d+)',data):
				stream = urllib.unquote(n.group('url'))
				quality = '???'
				if n.group('q') in fmt_value.keys():
					quality = fmt_value[n.group('q')]
				if not quality in qualities:
					item = {}
					item['name'] = __name__
					item['url'] = stream
					item['quality'] = quality
					item['surl'] = url
					item['subs'] = ''
					qualities.append(quality)
					resolved.append(item)
			return resolved
		
# returns the steam url
def url(url):
	m = _regex(url)
	if not m == None:
		request = urllib.urlencode({'video_id':m.group('id'),'el':'embedded','asv':'3','hl':'en_US','eurl':__eurl__})
		data = util.request('http://www.youtube.com/get_video_info?%s' % request)
		data = urllib.unquote(util.decode_html(data))
		
		if data.find('status=fail') > -1:
			util.error('youtube resolver failed: '+data+' videoid:'+m.group('id'))
		else:
			stream = re.search('url_encoded_fmt_stream_map=url=(.+?)fallback_host',data,re.IGNORECASE | re.DOTALL).group(1)			
			return [urllib.unquote(stream)]

def _regex(url):
	return re.search('https?\://www\.youtube\.com/(watch\?v=|v/|embed/)(?P<id>.+?)(\?|$|&)',url,re.IGNORECASE | re.DOTALL)

