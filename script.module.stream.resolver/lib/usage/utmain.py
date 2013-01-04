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

__addon__ = xbmcaddon.Addon(id='script.module.stream.resolver')
__   = __addon__.getLocalizedString
import googletracker,tracker

def trackUsage(params):
    for param  in ['id','host','tc']:
        if not param in params:
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

    xbmc.log(msg='Parsed input params %s' % (str(params)),level=xbmc.LOGDEBUG)

    try:
        if not xbmcaddon.Addon(params['id']).getAddonInfo('id') == params['id']:
            raise Exception('')
    except:
        print 'Unable to create addon instance for %s, invalid addon ID?!' % (params['id'])
        return

    if register(params):		
        print 'Tracking usage ...'
        sett = tracker.TrackerSettings(__addon__)
        info = tracker.TrackerInfo().getSystemInfo()
        # retrieve per-installation-unique ID
        info['instanceid'] = sett.getInstanceID(params['service'])
        if 'google' == params['service']:
            return googletracker.track_usage(params['host'],params['action'],params['tc'],params['dry'],info)
    else:
        print 'Reporting for %s disabled by user' % (params['id'])

def register(params):
    sett = tracker.TrackerSettings(__addon__)
    enabled = sett.isReportingEnabled()
    if enabled == None:
        ret = xbmcgui.Dialog().yesno('XBMC Doplňky',__(30015))
        enabled = ret == 1
        sett.setReportingEnabled(enabled)
        sett.save()
    return enabled

def main(p={}):
    if 'do' in p:
        if p['do'] == 'reg':
            if not 'id' in p:
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


