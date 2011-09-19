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

# returns the steam url by searching for it in piece of HTML 
def url(data):
	m = re.search('value=\"http\://www.zkouknito.cz/(.+?)vid=(?P<id>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = util.request('http://www.zkouknito.cz/player/scripts/videoinfo_externi.php?id=%s' % m.group('id'))
		return re.search('<file>([^<]+)',data,re.IGNORECASE | re.DOTALL).group(1)

# returns the stream url directly from url found in HTML
def stream_url(url):
	m = re.search('zkouknito.cz/(.+?)vid=(?P<id>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = util.request('http://www.zkouknito.cz/player/scripts/videoinfo_externi.php?id=%s' % m.group('id'))
		return re.search('<file>([^<]+)',data,re.IGNORECASE | re.DOTALL).group(1)
