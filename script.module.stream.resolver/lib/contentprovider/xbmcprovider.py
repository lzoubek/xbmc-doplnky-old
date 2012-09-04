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

import sys,os,re,traceback,util,xbmcutil,search
import xbmcplugin,xbmc,xbmcgui

class XBMContentProvider(object):
	'''
	ContentProvider class provides an internet content. It should NOT have any xbmc-related imports
	and must be testable without XBMC runtime. This is a basic/dummy implementation.
	'''	
	
	def __init__(self,provider,settings,addon):
		'''
		XBMContentProvider constructor
		Args:
			name (str): name of provider
		'''
		self.provider = provider
		self.settings = settings
		self.addon = addon
		self.addon_id = addon.getAddonInfo('id')

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
		search.main(self.addon,'history',params,self.search)

	def root(self):
		if 'search' in self.provider.capabilities():
			search.item()
		xbmcutil.add_local_dir(xbmcutil.__lang__(30006),self.settings['downloads'],xbmcutil.icon('download.png'))	
		self.list(self.provider.categories())
		return xbmcplugin.endOfDirectory(int(sys.argv[1]))

	def download(self,url,name):
		downloads = self.settings['downloads']
		if '' == downloads:
			xbmcgui.Dialog().ok(self.provider.name,xbmcutil.__lang__(30009))
			return
		stream = self.resolve(url)
		if stream:
			xbmcutil.reportUsage(self.addon_id,self.addon_id+'/download')
			xbmcutil.download(self.addon,name,self.provider._url(stream['url']),os.path.join(downloads,name))
	
	def play(self,url):
		stream = self.resolve(url)
		if stream:
			xbmcutil.reportUsage(self.addon_id,self.addon_id+'/play')
			print 'Sending %s to player' % stream['url']
			li = xbmcgui.ListItem(path=stream['url'],iconImage='DefaulVideo.png')
			return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)	

	def resolve(self,url):
		return self.provider.resolve({'url':url})

	def search(self,keyword):
		self.list(self.provider.search(keyword))
		return xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
	def list(self,items):
		for item in items:
			if item['type'] == 'dir':
				self.render_dir(item)
			elif item['type'] == 'next':
				xbmcutil.add_dir(xbmcutil.__lang__(30007),{'list':item['url']},xbmcutil.icon('next.png'))
			elif item['type'] == 'prev':
				xbmcutil.add_dir(xbmcutil.__lang__(30008),{'list':item['url']},xbmcutil.icon('prev.png'))
			elif item['type'] == 'video':
				self.render_video(item)

	def render_dir(self,item):
		xbmcutil.add_dir(item['title'],{'list':item['url']},menuItems={xbmc.getLocalizedString(117):menuItems})

	def render_video(self,item):
		title = '%s (%s)' % (item['title'],item['size'])
		xbmcutil.add_video(title,
			{'play':item['url']},
			item['img'],
			infoLabels={'Title':item['title']},
			menuItems={xbmc.getLocalizedString(33003):{'name':item['title'],'down':item['url']}}
		)	
	
	def categories(self):
		self.list(self.provider.categories(keyword))
		return xbmcplugin.endOfDirectory(int(sys.argv[1]))

