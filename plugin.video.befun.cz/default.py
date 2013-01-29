# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Libor Zoubek
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
sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )
import befun
import xbmcprovider,xbmcaddon,xbmcutil,xbmc
import util
import traceback,urllib2

__scriptid__   = 'plugin.video.befun.cz'
__scriptname__ = 'befun.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

settings = {'downloads':__addon__.getSetting('downloads'),'quality':__addon__.getSetting('quality')}

class BefunXBMContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):

    def download(self,url,name):
        downloads = self.settings['downloads']
        if '' == downloads:
            xbmcgui.Dialog().ok(self.provider.name,xbmcutil.__lang__(30009))
            return
        stream = self.resolve(url)
        if stream:
            xbmcutil.reportUsage(self.addon_id,self.addon_id+'/download')
            if not stream['subs'] == '':
                util.save_to_file(stream['subs'],os.path.join(downloads,name+'.srt'))
            if stream['url'].find('munkvideo') > 0:
                # we have to handle this download a special way
                filename = xbmc.makeLegalFilename(os.path.join(downloads,name+'.mp4'))
                icon = os.path.join(__addon__.getAddonInfo('path'),'icon.png')
                output = open(filename,'wb')
                try:
                    req = urllib2.Request(stream['url'],headers={'Referer':'me'}) # that special way
                    response = urllib2.urlopen(req)
                    data = response.read(8192)
                    xbmc.executebuiltin('XBMC.Notification(%s,%s,3000,%s)' % (xbmc.getLocalizedString(13413).encode('utf-8'),filename,icon))
                    while len(data) > 0:
                        output.write(data)
                        data = response.read(8192)
                    response.close()
                    output.close()
                    if xbmc.Player().isPlaying():
                        xbmc.executebuiltin('XBMC.Notification(%s,%s,8000,%s)' % (xbmc.getLocalizedString(20177),filename,icon))
                    else:
                        xbmcgui.Dialog().ok(xbmc.getLocalizedString(20177),filename)
                except:
                    traceback.print_exc()
                    xbmc.executebuiltin('XBMC.Notification(%s,%s,5000,%s)' % (xbmc.getLocalizedString(257),filename,icon))
                    xbmcgui.Dialog().ok(filename,xbmc.getLocalizedString(257))
                    output.close()
            else:
                xbmcutil.download(self.addon,name,self.provider._url(stream['url']),os.path.join(downloads,name))


params = util.params()
if params=={}:
    xbmcutil.init_usage_reporting( __scriptid__)
BefunXBMContentProvider(befun.BefunContentProvider(),settings,__addon__).run(params)
