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

def supports(url):
	return not _regex(url) == None

def url(url):
	if not _regex(url) == None:
		data = util.request(url)
		data = util.substr(data,'div id=\"playerWrap\"','<embed>')
		if len(data) > 0:
			host = re.search('host=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
			oid = re.search('oid=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
			vtag = re.search('vtag=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
			hd = re.search('hd_def=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
			no_flv = re.search('no_flv=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
			url = '%su%s/video/%s' % (host,oid,vtag)
			if no_flv != '1':
				return [url+'.flv']
			if no_flv == '1' and int(hd) >= 0:
				resolutions=['240','360','480','720','1080']
				return [url+'.'+resolutions[int(hd)]+'.mp4']

def _regex(data):
	return re.search('http\://(vkontakte.ru|vk.com)/(.+?)', data, re.IGNORECASE | re.DOTALL)
