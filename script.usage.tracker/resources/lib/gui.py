#/*
# *      Copyright (C) 2010 lzoubek
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
import sys,os,time,re,traceback
import xbmc,xbmcaddon,xbmcgui,xbmcplugin

import tracker

ADDONS = 1001

class MainWindow ( xbmcgui.WindowXMLDialog ) :

	def __init__( self, *args, **kwargs ):
		super(xbmcgui.WindowXMLDialog, self).__init__(args,kwargs)
		self.trSettings = tracker.TrackerSettings(__addon__)

	def onFocus (self,controlId ):
		self.controlId=controlId

	def onInit (self):
		self._refresh_addons()
		self._refresh_addon_details()

	def _refresh_addons(self):
		list = self.getControl(ADDONS)
		list.reset()
		for add in self.trSettings.getSubscribers():
			add_inst = xbmcaddon.Addon(id=add)
			li = xbmcgui.ListItem(label=add_inst.getAddonInfo('name'),iconImage=add_inst.getAddonInfo('icon'))
			li.setProperty('id',add)
			enabled = self.trSettings.canDoReport(add)
			if enabled:
				enStr = __addon__.getLocalizedString(30004)
			else:
				enStr = __addon__.getLocalizedString(30005)
			print enStr
			li.setProperty('enabled',enStr)
			if enabled:
				li.setProperty('isenabled','True')
			termsID = self.trSettings.getTermsStringID(add)
			if termsID < 0:
				# use defaults
				terms = __addon__.getLocalizedString(30000) % (add_inst.getAddonInfo('name'),'')
			else:
				terms = __addon__.getLocalizedString(30000)% (add_inst.getAddonInfo('name'),add_inst.getLocalizedString(termsID))
			li.setProperty('terms',terms)
			list.addItem(li)

	def _refresh_addon_details(self):
		print 'refresh'
		selected = self.getControl(ADDONS).getSelectedItem()

	def onAction(self, action):
		#print 'Action id=%s buttonCode=%s amount1=%s amount2=%s' % (action.getId(),action.getButtonCode(),action.getAmount1(),action.getAmount2())
		if action.getId() in [9,10]:
			self.close()
		if action.getId() in [3,4] and self.getFocusId() == ADDONS:
			self._refresh_addon_details()
			
#	if str(action.getId()) in ACTIONS:
#			command = ACTIONS[str(action.getId())]
#			print 'action: '+command
#			self._exec_command(command)

	def onClick( self, controlId ):
		print controlId
		if controlId in [1003, 1001]:
			selected_index = self.getControl(ADDONS).getSelectedPosition()
			addon = self.getControl(ADDONS).getSelectedItem().getProperty('id')
			add_inst = xbmcaddon.Addon(addon)
			isenabled = self.getControl(ADDONS).getSelectedItem().getProperty('isenabled') == 'True'
			if isenabled:
				ret = xbmcgui.Dialog().yesno(__addon__.getAddonInfo('name'),(__addon__.getLocalizedString(30007) % add_inst.getAddonInfo('name')))
			else:
				ret = xbmcgui.Dialog().yesno(__addon__.getAddonInfo('name'),(__addon__.getLocalizedString(30006) % add_inst.getAddonInfo('name')))
			
			confirmed = ret == 1
			if confirmed:
				self.trSettings.setCanReport(addon,not isenabled)
				self.trSettings.save()
				self._refresh_addons()
				self.getControl(ADDONS).selectItem(selected_index)
		elif controlId == 1000:
			__addon__.openSettings()
#		if str(controlId) in CLICK_ACTIONS:
#			command = CLICK_ACTIONS[str(controlId)]
#			print 'click action: '+command
#			self._exec_command(command)
