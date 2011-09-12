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
from htmlentitydefs import name2codepoint as n2cp
import urllib2,re,os
import xbmcaddon,xbmc,xbmcgui,xbmcplugin

__scriptid__   = 'plugin.video.serialycz.cz'
__scriptname__ = 'serialycz.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.serialycz.cz/'

def request(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def add_dir(name,id,logo):
	logo = replace(logo)
	name = _decode_html(replace(name,None,'No name'))
        u=sys.argv[0]+"?"+id
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=logo)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def replace(obj,what=None,replacement=''):
	if obj == what:
		return replacement
	return obj

def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()

def _decode_html(data):
	try:
		entity_re = re.compile(r'&(#?)(x?)(\w+);')
    		return entity_re.subn(substitute_entity, data.decode('utf-8'))[0]
	except:
		return data

def get_substr(data,start,end):
	i1 = data.find(start)
	i2 = data.find(end,i1)
	return data[i1:i2]

def get_params():
        param={}
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
	return param

def add_stream(name,url,bitrate,logo):
	bit = 0
	try:
		bit = int(bitrate)
	except:
		pass
	name = _decode_html(replace(name,None,'No name'))
	if bit > 0:
		name = "%s | %s kbps" % (name,bit)
	logo = replace(logo)
	url=sys.argv[0]+"?play="+url.replace('?','!').replace('=','#')
	li=xbmcgui.ListItem(name,path = url,iconImage="DefaultVideo.png",thumbnailImage=logo)
        li.setInfo( type="Video", infoLabels={ "Title": name} )
	li.setProperty("IsPlayable","true")
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def _image(name,link):
	# load image from disk or download it (slow for each serie, thatwhy we cache it)
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,name+'.png')
	if os.path.exists(local):
		return local
	else:
		data = get_substr(request(link),'<div id=\"archive-posts\"','</div>')
		m = re.search('<img(.+?)src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			print ' Downloading %s' % m.group('img')
			data = request(m.group('img'))
			f = open(local,'w')
			f.write(data)
			f.close()
			return local

def list_series():
	data = get_substr(request(BASE_URL),'<div id=\"primary\"','</div>')
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	for m in re.finditer(pattern, get_substr(data,'Seriály</a>','</ul>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'),'serie='+m.group('link')[len(BASE_URL):],_image(m.group('name'),m.group('link')))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_episodes(url):	
	data = request(BASE_URL+url)
	data = get_substr(data,'<div id=\"archive-posts\"','</div>')
	m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = request(m.group('url'))
		for m in re.finditer('<a href=\"(?P<link>[^\"]+)(.+?)<strong>(?P<name>[^<]+)', get_substr(data,'<div class=\"entry-content','</div>'), re.IGNORECASE | re.DOTALL):
			add_stream(m.group('name'),m.group('link')[len(BASE_URL):],0,'')
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	url = url.replace('!','?').replace('#','=')
	for gen in resolve_stream(url):
		for url in gen:
			if url == '':
				return
			print 'Sending %s to player' % url
			li = xbmcgui.ListItem(path=url,iconImage='DefaulVideo.png')
			return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(__scriptname__,'Prehravani vybraneho videa bud neni[CR]podporovano nebo video neni k dispozici.')

def resolve_stream(url):
	data = request(BASE_URL+url)
	data = get_substr(data,'<div id=\"content\"','<div id=\"sidebar')
	for f in [_vk,_weed,_zkouknito,_videotube]:
		yield f(data)
def _videotube(data):
	m = re.search('src=\"(?P<js>http\://www.videotube.sk/js[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		#data = request(m.group('js'))
		xbmcgui.Dialog().ok(__scriptname__,'Video neni mozne prehrat,[CR]zdroj videotube.sk neni podporovan')
		yield ''

def _zkouknito(data):
	m = re.search('value=\"http\://www.zkouknito.cz/(.+?)vid=(?P<id>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = request('http://www.zkouknito.cz/player/scripts/videoinfo_externi.php?id=%s' % m.group('id'))
		yield re.search('<file>([^<]+)',data,re.IGNORECASE | re.DOTALL).group(1)
	

def _vk(data):
	m = re.search('<iframe src=\"(?P<url>http\://(vkontakte.ru|vk.com)[^\"]+)(.+?)height=\"(?P<height>[\d]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = request(m.group('url').replace('&#038;','&'))
		data = get_substr(data,'div id=\"playerWrap\"','<embed>')
		host = re.search('host=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		oid = re.search('oid=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		vtag = re.search('vtag=([^\&]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		yield '%su%s/video/%s.%s.mp4' % (host,oid,vtag,m.group('height'))

def _weed(data):
	m = re.search('<iframe(.+?)src=\'(?P<url>http\://embed.videoweed.com[^\']+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = request(m.group('url').replace('&#038;','&'))
		data = get_substr(data,'flashvars','params')
		domain = re.search('flashvars\.domain=\"([^\"]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		file = re.search('flashvars\.file=\"([^\"]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		key = re.search('flashvars\.filekey=\"([^\"]+)',data,re.IGNORECASE | re.DOTALL).group(1)
		data = request('%s/api/player.api.php?key=%s&file=%s&user=undefined&codes=undefined&pass=undefined'% (domain,key,file))
		m = re.search('url=(?P<url>[^\&]+)',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			yield m.group('url')

params=get_params()
if params=={}:
	list_series()
if 'serie' in params.keys():
	list_episodes(params['serie'])
if 'play' in params.keys():
	play(params['play'])
