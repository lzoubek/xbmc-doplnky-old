# -*- coding: UTF-8 -*-
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

# thanks to:
#   https://github.com/Eldorados


import re,util,urllib2
__name__='flashx'

pattern = 'http://((?:www.|play.)?flashx.tv)/(?:player/embed_player.php\?vid=|player/embed.php\?vid=|player/embed.php\?hash=|video/)([0-9A-Z]+)'

def supports(url):
	return not _regex(url) == None
	
	
def get_url(host, media_id):
        return 'http://www.flashx.tv/player/embed_player.php?vid=%s' % (media_id)


def get_host_and_id(url):
        r = re.search(pattern, url)
        if r:
		return r.groups()
        else:
		return False
	
# returns the steam url
def url(url):
	if supports(url):
		host,media_id=get_host_and_id(url)
		web_url = get_url(host, media_id)
		try:
			data = util.request(web_url)
		except urllib2.URLError, e:
			print (__name__ + ': got http error %d fetching %s' % (e.code, web_url))
			return False
		sPatternHQ = "var hq_video_file\s*=\s*'([^']+)'"        # .mp4
		sPatternLQ = "\?hash=([^'|&]+)"
		r = re.search(sPatternLQ, data)
		if r:
			#print r.group(1)
			media_id = r.group(1)
			#return r.group(1)
		try:
			data = util.request("http://play.flashx.tv/nuevo/player/cst.php?hash="+media_id)
		except urllib2.URLError, e:
			print (__name__ + ': got http error %d fetching %s' % (e.code, web_url))
			return False
		pattern = "<file>(.*?)</file>"
		r = re.search(pattern, data)
		if r:
			return [r.group(1)]

		return False
		
		

def resolve(u):
	stream = url(u)
	if stream:
		return [{'name':__name__,'quality':'360p','url':stream[0],'surl':u}]

def _regex(url):
	return re.search(pattern,url,re.IGNORECASE | re.DOTALL)
	
	
