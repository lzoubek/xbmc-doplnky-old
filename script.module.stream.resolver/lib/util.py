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
import os,re,sys,urllib,urllib2,traceback,cookielib,time,socket
import xbmcgui,xbmcplugin,xbmc
from htmlentitydefs import name2codepoint as n2cp
import simplejson as json
UA='Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'

##
# initializes urllib cookie handler
def init_urllib():
	cj = cookielib.LWPCookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	urllib2.install_opener(opener)

def request(url,headers={}):
	debug('request: %s' % url)
	req = urllib2.Request(url,headers=headers)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	debug('len(data) %s' % len(data))
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

def add_local_dir(name,url,logo='',infoLabels={}):
	name = decode_html(name)
	infoLabels['Title'] = name
	liz=xbmcgui.ListItem(name, iconImage='DefaultFolder.png',thumbnailImage=logo)
        liz.setInfo( type='Video', infoLabels=infoLabels )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=True)

def add_video(name,params={},logo='',infoLabels={},menuItems={}):
	name = decode_html(name)
	infoLabels['Title'] = name
	url = _create_plugin_url(params)
	li=xbmcgui.ListItem(name,path=url,iconImage='DefaultVideo.png',thumbnailImage=logo)
        li.setInfo( type='Video', infoLabels=infoLabels )
	li.setProperty('IsPlayable','true')
	items = []
	for mi in menuItems.keys():
		items.append((mi,'RunPlugin(%s)'%_create_plugin_url(menuItems[mi])))
	if len(items) > 0:
		li.addContextMenuItems(items)
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def _create_plugin_url(params):
	url=[]
	for key in params.keys():
		value = decode_html(params[key])
		value = value.encode('ascii','ignore')
		url.append(key+'='+value.encode('hex',)+'&')
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
		if not type(data) == unicode:
			data = unicode(data,'utf-8',errors='ignore')
		entity_re = re.compile(r'&(#?)(x?)(\w+);')
    		return entity_re.subn(_substitute_entity,data)[0]
	except:
		traceback.print_exc()
		print [data]
		return data

def debug(text):
	xbmc.log(text,xbmc.LOGDEBUG)

def info(text):
	xbmc.log(text)

def error(text):
	xbmc.log(text,xbmc.LOGERROR)


def get_searches(addon,server):
	local = xbmc.translatePath(addon.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,server)
	if not os.path.exists(local):
		return []
	f = open(local,'r')
	data = f.read()
	searches = json.loads(unicode(data.decode('utf-8','ignore')))
	f.close()
	return searches

def add_search(addon,server,search,maximum):
	searches = []
	local = xbmc.translatePath(addon.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,server)
	if os.path.exists(local):
		f = open(local,'r')
		data = f.read()
		searches = json.loads(unicode(data.decode('utf-8','ignore')))
		f.close()
	if search in searches:
		searches.remove(search)
	searches.insert(0,search)
	remove = len(searches)-maximum
	if remove>0:
		for i in range(remove):
			searches.pop()
	f = open(local,'w')
	f.write(json.dumps(searches,ensure_ascii=True))
	f.close()

def download(addon,filename,url,local):
	icon = os.path.join(addon.getAddonInfo('path'),'icon.png')
	notify = addon.getSetting('download-notify') == 'true'
	notifyEvery = addon.getSetting('download-notify-every')
	notifyPercent = 1
	if int(notifyEvery) == 0:
		notifyPercent = 10
	if int(notifyEvery) == 1:
		notifyPercent = 5
	def callback(percent,speed,filename):
		if percent == 0 and speed == 0:
			xbmc.executebuiltin('XBMC.Notification(%s,%s,3000,%s)' % (xbmc.getLocalizedString(259).encode('utf-8'),filename,icon))
			return
		if notify:
			if percent > 0 and percent % notifyPercent == 0:
				message = xbmc.getLocalizedString(24042) % percent + ' - %s KB/s' %speed
				xbmc.executebuiltin('XBMC.Notification(%s,%s,5000,%s)'%(message.encode('utf-8'),filename,icon))

	downloader = Downloader(callback)
	result = downloader.download(url,local,filename)
	if result == True:
		xbmc.executebuiltin('XBMC.Notification(%s,%s,5000,%s)' % (xbmc.getLocalizedString(20177),filename,icon))
	else:
		xbmc.executebuiltin('XBMC.Notification(%s,%s,5000,%s)' % (xbmc.getLocalizedString(257),filename,icon))
		xbmcgui.Dialog().ok(filename,xbmc.getLocalizedString(257) +' : '+result)

class Downloader(object):
	def __init__(self,callback = None):
		self.init_time = time.time()
		self.callback = callback
		self.gran = 50
		self.percent = -1

	def download(self,remote,local,filename=None):
		class MyURLopener(urllib.FancyURLopener):
			def http_error_default(self, url, fp, errcode, errmsg, headers):
				self.error_msg = 'Downlad failed, error : '+str(errcode)

		if not filename:
			filename = os.path.basename(local)
		self.filename = filename
		if self.callback:
			self.callback(0,0,filename)
		socket.setdefaulttimeout(60)
		opener = MyURLopener()
		try:
			opener.retrieve(remote,local,reporthook=self.dlProgress)
			if hasattr(opener,'error_msg'):
				return opener.error_msg
			return True
		except socket.error:
			errno, errstr = sys.exc_info()[:2]
			if errno == socket.timeout:
				return 'Download failed, connection timeout'
		except:
			traceback.print_exc()
			errno, errstr = sys.exc_info()[:2]
			return str(errstr)

	def dlProgress(self,count, blockSize, totalSize):
		if count % self.gran == 0 and not count == 0:
			percent = int(count*blockSize*100/totalSize)
			downloaded = int(count*blockSize)
			newTime = time.time()
			diff = newTime - self.init_time
			self.init_time = newTime
			speed = int(((1/diff) * blockSize * self.gran )/1024)
			if self.callback and not self.percent == percent:
				self.callback(percent,speed,self.filename)
			self.percent=percent
