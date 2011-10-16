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
# */ based on script.module.dmd-czech.common/lib/videobb.py

import util,re,base64

def supports(url):
	return not _regex(url) == None

def url(url):
	m = _regex(url)
	if not m == None:
		util.init_urllib()
		data = util.request('http://videobb.com/player_control/settings.php?v=%s&em=TRUE&fv=v1.1.67' % m.group('id'))
		data = data.replace('false','False').replace('true','True').replace('null','None')
		json = eval('('+data+')')
		return [base64.decodestring(json['settings']['res'][-1]['u'])]

def _regex(url):
	return re.search('http://(www\.)?videobb.com/[\w\d]+/(?P<id>[^$]+)', url, re.IGNORECASE | re.DOTALL)
