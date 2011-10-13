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

import urllib2,re,os,random
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util,resolver

__scriptid__   = 'plugin.video.zapni.tv'
__scriptname__ = 'zapni.tv'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://zapni.tv/'

def parse_asx(url):
	if not url.endswith('asx'):
		return url
	data = util.request(url)
	refs = re.compile('.*<Ref href = \"([^\"]+).*').findall(data,re.IGNORECASE|re.DOTALL|re.MULTILINE)
	urls = []
	for ref in refs:
		stream = parse_asx(ref)
		urls.append(stream.replace(' ','%20'))
	if urls == []:
		print 'Unable to parse '+url
		print data
		return ''
	return urls[-1]

def add_stream(name,url,bitrate,logo):
	bit = 0
	try:
		bit = int(bitrate)
	except:
		pass
	if bit > 0:
		name = "%s | %s kbps" % (name,bit)
	return util.add_video(name,{'play':url},logo)

def list_categories():
	data = util.request(BASE_URL)
	pattern='<li><a onmousedown=\'[^\']+\'( class=\'divider\')? href=\'kat\.php\?id=(?P<link>[^\']+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, util.substr(data,'<li class=\'menu\'><p>Kategorie</p>','</ul>'), re.IGNORECASE | re.DOTALL):
		if m.group('link').find('porno') > 0:
			continue
		util.add_dir(m.group('cat'),{'cat':m.group('link')})
	util.add_dir('Ostatní',{'cat':''})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_category(id):	
	data = util.request(BASE_URL+'kat.php?id='+id)
	data = util.substr(data,'class=\'centerContent\'','<p class=\'strankovani\'>')
	pattern='<a href=\"play.php\?id=(?P<id>[^\"]+)[^>] title=\"(?P<name>[^\"]+)\"><img align=\"left\" style=\"[^\']+\'(?P<img>[^\']+)[^>]+></a>[^\:]+\:[ ]?<b>(?P<bitrate>[\d]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_stream(m.group('name'),m.group('id'),m.group('bitrate'),BASE_URL+m.group('img'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(id):
	url = resolve_stream(id)
	if not url == None:
		print 'Sending %s to player' % url
		li = xbmcgui.ListItem(path=url,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(__scriptname__,__language__(30000))

def resolve_stream(id):
	data = util.request(BASE_URL+'play.php?id='+id)
	data = util.substr(data,'class=\'centerContent\'','class=\'side-border-right\'')
	for f in [_wmp,_rp,_vlc,_flash_zakladni,_flash_pls,_seeon,_borec,_apache_cz]:
		url = f(data)
		if not url == None:
			return url

def _rp(data):
	m = re.search('<embed type=\"audio/x-pn-realaudio-plugin\" src=\"(?P<url>stream/real.php[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		return BASE_URL+m.group('url')

def _vlc(data):
	m = re.search('<br><a href=\"(?P<url>stream/vlc[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		url = BASE_URL+m.group('url')
		li = xbmcgui.ListItem(label='Zacatek',path='http://www.zapni.tv/stream/videa/zacatek.wmv')
		playlist.add('http://www.zapni.tv/stream/videa/zacatek.wmv',li,0)
		for i in range(0,3):
			li = xbmcgui.ListItem(label='Stream',path=url)
			playlist.add(url,li,0)
		return url

def _flash_pls(data):
	m = re.search('flashvars=\'playlistfile=(?P<url>[^\\&]+)',util.substr(data,'<embed','/>'), re.IGNORECASE | re.DOTALL)
	if not m == None:
		# there is a file in RSS playlist format, we need to get it, parse and pass it to video playlist
		pls = util.request(BASE_URL+m.group('url'))
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		count = 0
		url = ''
		for m in re.finditer('<item>[^<]+<title>(?P<title>[^<]+)</title>[^<]+<link>[^<]+</link>[^<]+<description>(?P<desc>[^<]+)</description>[^<]+<media\:group>[^<]+<media\:content url=\"(?P<url>[^\"]+)', pls, re.IGNORECASE | re.DOTALL):
			if count > 0:
				li = xbmcgui.ListItem(label='%s - %s'%(m.group('title'),m.group('desc')),path=m.group('url'))
				playlist.add(m.group('url'),li,0)
			if count > 1:
				url = m.group('url')
			count+=1
		return url

def _flash_zakladni(data):
	m = re.search('<embed src=\"(\\./)?stream/zakladni.swf\"(.+?)flashvars=\"file=(?P<url>[^\\&]+)',data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		return m.group('url')

def _seeon(data):
	m = re.search('<iframe src=\'http\://www.seeon.tv(.+?)channel=(?P<id>[\d]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		url = 'http://www.seeon.tv/view/'+m.group('id')
		html = util.request(url)
		swf_url, play = re.search('data="(.+?)".+?file=(.+?)\.flv', html, re.DOTALL).group(1, 2)
		rtmp = 'rtmp://live%d.seeon.tv/edge' % (random.randint(1, 10)) 
		rtmp += '/%s swfUrl=%s pageUrl=%s tcUrl=%s' % (play, swf_url, url, rtmp)
		return rtmp
def _apache_cz(data):
	# not yet working
	m = re.search('src=\"http\://www\.server-apache\.cz(.+?)(?P<url>rtmp\://[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		return m.group('url')
def _borec(data):
	m = re.search('open\(\"http://televize.borec.cz/\?id=(?P<id>[^\"]+)\"', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		return 'http://cdn.livestream.com/grid/LSPlayer.swf?channel=%s&autoPlay=true'%m.group('id')

def _wmp(data):
	m = re.search('<param name=\"url\" value=\"(?P<url>stream/wmp\.php[^\"]+)\">', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		return parse_asx(BASE_URL+m.group('url'))
	
params=util.params()
if params=={}:
	list_categories()
if 'cat' in params.keys():
	list_category(params['cat'])
if 'play' in params.keys():
	play(params['play'])
