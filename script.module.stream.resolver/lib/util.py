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
import os,re,sys,urllib,urllib2,traceback,cookielib
import xbmcgui,xbmcplugin,xbmc

UA='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

##
# initializes urllib cookie handler
def init_urllib():
	cj = cookielib.LWPCookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	urllib2.install_opener(opener)

def request(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def post(url,data):
	postdata = urllib.urlencode(data)
	req = urllib2.Request(url,postdata)
	req.add_header('User-Agent',UA)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def substr(data,start,end):
	i1 = data.find(start)
	i2 = data.find(end,i1)
	return data[i1:i2]

def add_dir(name,params,logo='',infoLabels={}):
	name = decode_html(name)
	infoLabels['Title'] = name
	liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png',thumbnailImage=logo)
        liz.setInfo( type='Video', infoLabels=infoLabels )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=_create_plugin_url(params),listitem=liz,isFolder=True)

def add_video(name,params={},logo='',infoLabels={}):
	name = decode_html(name)
	infoLabels['Title'] = name
	url = _create_plugin_url(params)
	li=xbmcgui.ListItem(name,path=url,iconImage='DefaultVideo.png',thumbnailImage=logo)
        li.setInfo( type='Video', infoLabels=infoLabels )
	li.setProperty('IsPlayable','true')
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def _create_plugin_url(params):
	url=[]
	for key in params.keys():
		value = decode_html(params[key].replace('&amp;','&').replace('&#038;','&'))
		url.append(key+'='+value.encode('hex')+'&')	
	return sys.argv[0]+'?'+''.join(url)
	

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
		param[p] = param[p].decode('hex')
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

def debug(text):
	xbmc.log(text,xbmc.LOGDEBUG)

def info(text):
	xbmc.log(text)

def error(text):
	xbmc.log(text,xbmc.LOGERROR)

