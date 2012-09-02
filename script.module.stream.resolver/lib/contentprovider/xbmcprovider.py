# *      Copyright (C) 2012 Libor Zoubek
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

import sys,os,re,traceback,util,xbmcutil

sys.path.append( os.path.join ( os.path.dirname(__file__),'contentprovider') )
class XBMContentProvider(object):
	'''
	ContentProvider class provides an internet content. It should NOT have any xbmc-related imports
	and must be testable without XBMC runtime. This is a basic/dummy implementation.
	'''	
	
	def __init__(self,provider,settings):
		'''
		XBMContentProvider constructor
		Args:
			name (str): name of provider
		'''
		self.provider = provider
		self.settings = settings

	def run(self,params):
		if params == {}:
			return self.root()
		if 'list' in params.keys():
			self.list(self.provider.list(params['list']))
			return xbmcplugin.endOfDirectory(int(sys.argv[1]))
			
		if 'down' in params.keys():
			return self.download(params['down'],params['name'])
		if 'play' in params.keys():
			return self.play(params['play'])

	def root(self):
		if 'search' in self.provider.categories():
			search.item()
		util.add_local_dir(__language__(30037),self.settings['downloads'],util.icon('download.png'))	
		self.list(self.provider.categories())
		return xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def download(self,url,name):
		pass
	
	def play(self,url):
		pass	

	def video_item(self):
		'''
		returns empty video item - contains all required fields
		'''
		return {'type':'video','title':'','rating':0,'year':0,'size':'0MB','url':'','img':'','length':'','quality':'???','subs':'','surl':''}

	def dir_item(self):
		'''
			reutrns empty directory item
		'''
		return {'type':'dir','title':'','size':'0','url':''}


	def search(self,keyword):
		'''
		Search for a keyword on a site
		Args:
            		keyword (str)

		returns:
			array of video or directory items
		'''
		return []
	
	def list(self,items):
		'''
		Lists content on given url
		Args:
            		url (str): either relative or absolute provider URL
			filter (function{item}) - a filter function that takes 1 argument (a video item) and returns True for accepting such item
		'''
		for item in items:
			if item['type'] == 'dir':
				render_dir(item)
			elif item['type'] = 'next':
				util.add_dir(util.__language__(30008),{'list':item['url']},util.icon('next.png'))
			elif item['type'] = 'prev':
				util.add_dir(util.__language__(30007),{'list':item['url']},util.icon('prev.png'))
			elif item['type'] = 'video':
				pass

	def render_dir(self,item):
		util.add_dir(item['title'],{'list':item['url']},menuItems={xbmc.getLocalizedString(117):menuItems})

	def render_video(self,item):
		pass
	
	def categories(self):
		'''
		Lists categories on provided site

		Returns:
			array of video or directory items
		'''
		return []

	def resolve(self,item,captcha_cb=None):
		'''
		Resolves given video item  to a downloable/playable file/stream URL
	
		Args:
			url (str): relative or absolute URL to be resolved
			captcha_cb(func{obj}): callback function when user input is required (captcha, one-time passwords etc).
			function implementation must be Provider-specific
		Returns:
			None - if ``url`` was not resolved. Video item with 'url' key pointing to resolved target
		'''
		return None

