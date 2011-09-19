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
import re,util
def url(data):
	m = re.search('<iframe src=\"(?P<url>http\://(vkontakte.ru|vk.com)[^\"]+)(.+?)height=\"(?P<height>[\d]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = util.request(m.group('url').replace('&#038;','&'))
		data = util.substr(data,'div id=\"playerWrap\"','<embed>')
		host = re.search('host=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		oid = re.search('oid=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		vtag = re.search('vtag=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		return '%su%s/video/%s.%s.mp4' % (host,oid,vtag,m.group('height'))
