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

__eurl__ = ''

def supports(url):
	return not _regex(url) == None

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
	return re.search('https?\://www\.youtube\.com/(watch\?v=|v/|embed/)(?P<id>.+?)($|&)',url,re.IGNORECASE | re.DOTALL)

