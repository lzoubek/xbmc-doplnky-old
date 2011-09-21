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
import re,sys,urllib2,traceback
import xbmcgui,xbmcplugin
import zkouknito,videoweed,vkontakte,videobb

def request(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def substr(data,start,end):
	i1 = data.find(start)
	i2 = data.find(end,i1)
	return data[i1:i2]

def resolve_stream(url):
	print 'Resolving '+url
	return _get_resolver(url)(url)

def _get_resolver(url):	
	for m in [zkouknito,videoweed,vkontakte,videobb]:
		if m.supports(url):
			return m.url
	return _dummy_resolver

def _dummy_resolver(url):
	return None

# returns true iff we are able to resolve stream by given URL
def can_resolve(url):
	return not _get_resolver(url) == None

def add_dir(name,url,logo='',infoLabels={}):
	name = decode_html(name)
	infoLabels['Title'] = name
        u=sys.argv[0]+'?'+url
	liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png',thumbnailImage=logo)
        liz.setInfo( type='Video', infoLabels=infoLabels )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def add_video(name,url,bitrate='',logo='',infoLabels={}):
	bit = 0
	try:
		bit = int(bitrate)
	except:
		pass
	name = decode_html(name)
	infoLabels['Title'] = name
	if bit > 0:
		name = '%s | %s kbps' % (name,bit)
	url=sys.argv[0]+'?play='+url.replace('?','!').replace('=','#')
	li=xbmcgui.ListItem(name,path = url,iconImage='DefaultVideo.png',thumbnailImage=logo)
        li.setInfo( type='Video', infoLabels=infoLabels )
	li.setProperty('IsPlayable','true')
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def params():
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
	for p in param.keys():
		param[p] = param[p].replace('!','?').replace('#','=')
	return param

def _substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == '#':
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

def decode_html(data):
	try:
		entity_re = re.compile(r'&(#?)(x?)(\w+);')
    		return entity_re.subn(_substitute_entity, data.decode('utf-8'))[0]
	except:
		traceback.print_exc()
		return data



