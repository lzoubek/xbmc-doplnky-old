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
import re,urllib,urllib2,random,util,sys,os
import xbmc,xbmcplugin,xbmcgui
def supports(url):
	return not _regex(url) == None

def _get_file_url(post_url):
	request = urllib.urlencode({'captcha_nb':__addon__.getSetting('captcha-id'),'captcha_user':__addon__.getSetting('captcha-key')})
	defrhandler = urllib2.HTTPRedirectHandler
	redirecthandler = MyHTTPRedirectHandler()
	opener = urllib2.build_opener(redirecthandler)
	urllib2.install_opener(opener)
	req = urllib2.Request(post_url,request)
	req.add_header('User-Agent',util.UA)
	try:
		resp = urllib2.urlopen(req)
	except urllib2.HTTPError:
		pass
	stream = redirecthandler.location
	urllib2.install_opener(urllib2.build_opener(defrhandler))
	if stream.find('full=y') > -1:
		util.error('[uloz.to] - out of free download slots, use payed account or try later')
		return -1
	if stream.find('neexistujici') > -1:
		util.error('[uloz.to] - movie was not found on server')
		return -2
	if stream.find('captcha=no') > -1:
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
	#return stream only when captcha was accepted and there
	return stream

# returns the steam url
def url(url):
	if supports(url):
		util.init_urllib()
		page = util.request(url)
		if page.find('Stránka nenalezena!') > 0:
			util.error('[uloz.to] - page with movie was not found on server')
			return -2
		data = util.substr(page,'<h3>Omezené stahování</h3>','<script')
		m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			return _get_file_url(m.group('action'))

def _regex(url):
	return re.search('(ulozto\.cz|uloz\.to)',url,re.IGNORECASE | re.DOTALL)

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):
		self.location = headers.getheader('Location')
		# this will lead to exception when 302 is recieved
		# exactly what we want - not to open url that's being redirected to

def search_list():
	util.add_dir(__language__(30004),{'search-ulozto':''},util.icon('search.png'))
	for what in util.get_searches(__addon__,'search_history_ulozto'):
		util.add_dir(what,{'search-ulozto':what})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def search(what):
	if what == '':
		kb = xbmc.Keyboard('',__language__(30003),False)
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

		util.add_search(__addon__,'search_history_ulozto',what,maximum)
		return list_page('http://www.ulozto.cz/hledej/?disclaimer=0&media=video&q='+urllib.quote(what))

def list_page(url):
	base_url = 'http://www.ulozto.cz'
	util.init_urllib()
	data = util.request(url+'&do=ajaxSearch',headers={'X-Requested-With':'XMLHttpRequest'})
	data = data.replace('null','None')
	page = eval(data)['snippets']['snippet--mainSearch'].replace('\\','')
	data = util.substr(page,'<ul class=\"thumbs','</ul>') 
	for m in re.finditer('<a href=\"(?P<url>[^\"]+)[^>]+>[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)alt=\"(?P<name>[^\"]+)(.+?)<span class=\"rght[^>]+>(?P<size>[^<]+)',data, re.IGNORECASE|re.DOTALL):
		iurl=base_url+m.group('url')
		util.add_video('%s (%s)' % (m.group('name'),m.group('size')),
			{'play':iurl},
			m.group('logo'),
			menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
			)
	# page naviagation
	data = util.substr(page,'<div class=\"paginator','</div')
	mprev = re.search('<a class=\"prev(.+?)href=\"(?P<url>[^\"]+)',data)
	if mprev:
		util.add_dir(__language__(30011),{'list-ulozto':base_url+mprev.group('url')},util.icon('prev.png'))
	mnext = re.search('<a class=\"next(.+?)href=\"(?P<url>[^\"]+)',data)
	if mnext:
		util.add_dir(__language__(30012),{'list-ulozto':base_url+mnext.group('url')},util.icon('next.png'))
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
