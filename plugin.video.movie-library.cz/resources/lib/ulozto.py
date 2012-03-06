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
import re,urllib,urllib2,random,util,sys,os,traceback
import xbmc,xbmcplugin,xbmcgui
def supports(url):
	return not _regex(url) == None

def full_url(url):
	if url.startswith('http'):
		return url
	return 'http://www.ulozto.cz/'+url.lstrip('/')

def _get_file_url(post_url):
	code = __addon__.getSetting('captcha-key')
	if len(code) < 1:
		# empty code in settings? set something to query user for beeter code
		code = 'abcd'
	request = urllib.urlencode({'captcha[id]':__addon__.getSetting('captcha-id'),'captcha[text]':code,'freeDownload':'Stáhnout'})
	defrhandler = urllib2.HTTPRedirectHandler
	redirecthandler = UloztoHTTPRedirectHandler()
	redirecthandler.location = None
	opener = urllib2.build_opener(redirecthandler)
	urllib2.install_opener(opener)
	req = urllib2.Request(post_url,request)
	req.add_header('User-Agent',util.UA)
	try:
		resp = urllib2.urlopen(req)
	except RedirectionException:
		# this is what we need, our redirect handler raises this
		pass
	except urllib2.HTTPError:
		# this is not OK, something went wrong
		traceback.print_exc()
		util.error('[uloz.to] cannot resolve stream url, server did not redirected us')
		util.info('[uloz.to] POST url:'+post_url)
		return
	stream = redirecthandler.location
	urllib2.install_opener(urllib2.build_opener(defrhandler))
	# we did not get 302 but 200
	if stream == None:
		cd = CaptchaDialog('captcha-dialog.xml',__addon__.getAddonInfo('path'),'default','0')
		captcha_id = str(random.randint(1,10000))
		cd.image = 'http://img.uloz.to/captcha/%s.png' % captcha_id
		cd.doModal()
		del cd
		kb = xbmc.Keyboard('',__addon__.getLocalizedString(200),False)
		kb.doModal()
		if kb.isConfirmed():
			code = kb.getText()
			__addon__.setSetting('captcha-id',captcha_id)
			__addon__.setSetting('captcha-key',code)
			return _get_file_url(post_url)
		else:
			return
	if stream.find('full=y') > -1:
		util.error('[uloz.to] - out of free download slots, use payed account or try later')
		return -1
	if stream.find('neexistujici') > -1:
		util.error('[uloz.to] - movie was not found on server')
		return -2
	#return stream only when captcha was accepted and there
	return stream

# returns the steam url
def url(url):
	if supports(url):
		util.init_urllib()
		try:
			page = util.request(url)
		except urllib2.HTTPError, e:
				traceback.print_exc()
				return -2
		if page.find('Stránka nenalezena!') > 0:
			util.error('[uloz.to] - page with movie was not found on server')
			return -2
		data = util.substr(page,'<h3>Omezené stahování</h3>','<script')
		m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			return _get_file_url(full_url(m.group('action')))

def _regex(url):
	return re.search('(ulozto\.cz|uloz\.to)',url,re.IGNORECASE | re.DOTALL)

class UloztoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):
		self.location = headers.getheader('Location')
		raise RedirectionException()
		# this will lead to exception when 302 is recieved
		# exactly what we want - not to open url that's being redirected to
	http_error_301 = http_error_303 = http_error_307 = http_error_302

class RedirectionException(Exception):
	pass

def search_list():
	util.add_dir(util.__lang__(30004),{'search-ulozto':''},util.icon('search.png'))
	for what in util.get_searches(__addon__,'search_history_ulozto'):
		util.add_dir(what,{'search-ulozto':what},menuItems={xbmc.getLocalizedString(117):{'search-ulozto-remove':what}})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def search_remove(search):
	util.remove_search(__addon__,'search_history_ulozto',search)
	xbmc.executebuiltin('Container.Refresh')

def search(params):
	what = params['search-ulozto']
	if what == '':
		kb = xbmc.Keyboard('',util.__lang__(30003),False)
		kb.doModal()
		if kb.isConfirmed():
			what = kb.getText()
	if not what == '':
		maximum = 20
		try:
			maximum = int(__addon__.getSetting('keep-searches'))
		except:
			util.error('Unable to parse convert addon setting to number')
			pass
		if not 'search-no-history' in params.keys():
			util.add_search(__addon__,'search_history_ulozto',what,maximum)
		return list_page('http://www.ulozto.cz/hledej/?media=video&q='+urllib.quote(what))

def list_page(url):
	util.init_urllib()
	page = util.request(url)
	data = util.substr(page,'<ul class=\"chessFiles','</ul>') 
	for m in re.finditer('<li>.+?<a href=\"(?P<url>[^\"]+)[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)alt=\"(?P<name>[^\"]+)(.+?)<span class=\"fileSize[^>]+>(?P<size>[^<]+)<span class=\"fileTime[^>]+>(?P<time>[^<]+)',data, re.IGNORECASE|re.DOTALL):
		iurl=full_url(m.group('url'))
		util.add_video('%s (%s | %s)' % (m.group('name'),m.group('size').strip(),m.group('time')),
			{'play':iurl},
			full_url(m.group('logo')),
			infoLabels={'Title':m.group('name')},
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
			)
	# page naviagation
	data = util.substr(page,'<div class=\"paginator','</div')
	mprev = re.search('<a href=\"(?P<url>[^\"]+)\" class=\"prev',data)
	if mprev:
		util.add_dir(__language__(30011),{'list-ulozto':full_url(mprev.group('url'))},util.icon('prev.png'))
	mnext = re.search('<a href=\"(?P<url>[^\"]+)\" class="next',data)
	if mnext:
		util.add_dir(__language__(30012),{'list-ulozto':full_url(mnext.group('url'))},util.icon('next.png'))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

class CaptchaDialog ( xbmcgui.WindowXMLDialog ):

	def __init__(self,*args,**kwargs):
		super(xbmcgui.WindowXMLDialog, self).__init__(args,kwargs)
		self.image = 'http://img.uloz.to/captcha/38470.png'

	def onFocus (self,controlId ):
		self.controlId = controlId

	def onInit (self ):
		self.getControl(101).setImage(self.image)

	def onAction(self, action):
		if action.getId() in [9,10]:
			self.close()

	def onClick( self, controlId ):
		if controlId == 102:
			self.close()
