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
import re,urllib,urllib2,random,util

def supports(url):
	return not _regex(url) == None

# returns the steam url
def url(url):
	if supports(url):
		util.init_urllib()
		page = util.request(url)
		data = util.substr(page,'<h3>Omezené stahování</h3>','<script')
		m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			captchas = {'4009':'zfpv','1987':'jllj','8743':'mubr','6188':'ggtc','6881':'lzhm','2160':'lnqe','594':'uhcd'}
			random_captcha = captchas.keys()[random.randint(0,len(captchas)-1)]
			request = urllib.urlencode({'captcha_nb':random_captcha,'captcha_user':captchas[random_captcha]})
			defrhandler = urllib2.HTTPRedirectHandler
			redirecthandler = MyHTTPRedirectHandler()
			opener = urllib2.build_opener(redirecthandler)
			urllib2.install_opener(opener)
			req = urllib2.Request(m.group('action'),request)
			req.add_header('User-Agent',util.UA)
			response = urllib2.urlopen(req)
			response.close()
			urllib2.install_opener(urllib2.build_opener(defrhandler))
			stream = redirecthandler.location
			if stream.find('full=y') > -1:
				util.error('[uloz.to] - out of free download slots, use payed account or try later')
				return -1
			if stream.find('captcha=no') > -1:
				util.error('[uloz.to] - error validating captcha, addon needs to be fixed')
				return
			#return stream only when captcha was accepted and there
			return stream

def _regex(url):
	return re.search('uloz\.to',url,re.IGNORECASE | re.DOTALL)

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):
		self.location = headers.getheader('Location')
		return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

