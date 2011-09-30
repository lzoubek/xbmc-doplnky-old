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

import re,util,base64


__PREFER_HD__=True

def supports(url):
	return not _regex(url) == None

def url(url):
	m = _regex(url)
	if not m == None:
		stream = None
		data = util.request('http://www.videozer.com/player_control/settings.php?v=%s&em=TRUE&fv=v1.1.12' % m.group('id'))
		data = eval(data.replace('true','True').replace('false','False').replace('null','None'))		
		if len(data['cfg']['quality']) > 0:
			stream = base64.encodestring(data['cfg']['quality'][0]['u'])
		for q in data['cfg']['quality']:
			if q['l'] == 'HQ' and __PREFER_HD__:
				return [base64.decodestring(q['u'])]
		if not stream == None:
			return [stream]

def _regex(url):
	return  re.search('videozer.com/embed/(?P<id>[_\-\w\d]+)',url,re.IGNORECASE | re.DOTALL)
