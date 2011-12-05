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
import xbmc,xbmcaddon,xbmcgui
__scriptid__   = 'script.usage.tracker'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__		= __addon__.getLocalizedString
sys.path.append( os.path.join (__addon__.getAddonInfo('path'), 'resources','lib'))

import google,tracker

def trackUsage(params):
	for param  in ['id','host','tc']:
		if not param in params:
			printHelp()
			raise Exception(param+' param is required')
	if not 'service' in params:
		params['service'] = 'google'
	if not 'cond' in params:
		params['cond'] = -1
	else:
		try:
			params['cond'] = int(params['cond'])
		except:
			pass
	if not 'action' in params:
		params['action'] = params['id']
	if 'dry' in params:
		try:
			params['dry'] = bool(params['dry'])
		except:
			params['dry'] = False
	else:
		params['dry'] = False
	
	xbmc.log(msg='[%s] Parsed input params %s' % (__scriptid__,str(params)),level=xbmc.LOGDEBUG)
	
	try:
		if not xbmcaddon.Addon(params['id']).getAddonInfo('id') == params['id']:
			raise Exception('')
	except:
		print '[%s] Unable to create addon instance for %s, invalid addon ID?!' % (__scriptid__,params['id'])
		return
	
	if register(params):
		print '[%s] Tracking usage ...' % __scriptid__
		sett = tracker.TrackerSettings(__addon__)
		info = tracker.TrackerInfo().getSystemInfo()
		info['instanceid'] = sett.getInstanceID(params['service'])
		if 'google' == params['service']:
			return google.track_usage(params['host'],params['action'],params['tc'],params['dry'],info)
	else:
		print '[%s] Reporting for %s disabled by user' % (__scriptid__,params['id'])

def register(params):
	sett = tracker.TrackerSettings(__addon__)
	canReport = sett.canDoReport(params['id'])
	if canReport == None:
		# we ask user
		ret = xbmcgui.Dialog().yesno(__addon__.getAddonInfo('name'),__(30001),__(30002),__(30003))
		canReport = ret == 1	
		# register addon with result
		sett.addAddon(params['id'],canReport,params['cond'])
		sett.save()
		print '[%s] addon %s registered with usage tracker' % (__scriptid__,params['id'])
	return canReport

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
	return param

def printHelp():
	print 'Usage Tracker script usage:'
	print 'Call script using xbmc.executebuiltin(\'RunPlugin(plugin://script.usage.tracker/?param1=value2&param2=value2)\')'
	print ''
	print 'Operations:'
	print 'do=track - default does tracking, does not need to be specified when tracking'
	print 'do=reg - only registers your addon with usage tracking addon - if it is for first time user is asked'
	print ''
	print 'Parameters:'
	print 'id=<caller plugin id> - required, it is used to determine whether usage reporting is enabled, also specifies default action'
	print 'host=<url> - required, URL to be tracked'
	print 'tc=<tracking code> - required, tracking code associated with host param'
	print 'service=google - optional, currently only google (default) service is supported, others may be added in future'
	print 'cond=<string ID> - optional, defines ID of String from caller plugin which contains info what and when can be tracked, this is displayed as Author\' note in script Usage Tracker UI'
	print 'action=<action> - optional, specifies request uri, that will be pinged'
	print 'dry=true|false - optional, if true, reporting itself will be disabled - useful for debugging'

def main():
	p = params()
	if 'do' in p:
		if p['do'] == 'reg':
			if not 'id' in p:
				printHelp()
				raise Exception('id param is required')
			if not 'cond' in p:
				p['cond'] = -1
			else:
				try:
					p['cond'] = int(p['cond'])
				except:
					pass
			return register(p)
	trackUsage(p)


if len(sys.argv)>1:
	main()
else:
	import gui
	gui.__addon__ = __addon__
	mw = gui.MainWindow('main-window.xml',__addon__.getAddonInfo('path'),'default','0')
	mw.doModal()
	del mw
