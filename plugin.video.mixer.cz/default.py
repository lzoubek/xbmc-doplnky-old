# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Maros Ondrasek
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

import os
import xbmcaddon
import resolver
import util,xbmcprovider,xbmcutil,xbmcgui, xbmcplugin

__scriptid__   = 'plugin.video.mixer.cz'
__scriptname__ = 'mixer.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

sys.path.append( os.path.join ( __addon__.getAddonInfo('path'), 'resources','lib') )
import mixercz
settings = {'downloads':__addon__.getSetting('downloads'),'quality':__addon__.getSetting('quality')}

class MixerczXBMCContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):

    def play(self, item):
        stream = self.resolve(item['url'])
        if type(stream) == type([]):
            # resolved to mutliple files, we'll feed playlist and play the first one
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            for video in stream:
                li = xbmcgui.ListItem(label=video['title'], path=video['url'], iconImage='DefaultVideo.png')
                playlist.add(video['url'], li)
            xbmc.Player().play(playlist)
        elif stream:
            xbmcutil.reportUsage(self.addon_id, self.addon_id + '/play')
            if 'headers' in stream.keys():
                for header in stream['headers']:
                    stream['url'] += '|%s=%s' % (header, stream['headers'][header])
            print 'Sending %s to player' % stream['url']
            li = xbmcgui.ListItem(path=stream['url'], iconImage='DefaulVideo.png')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
            xbmcutil.load_subtitles(stream['subs'])

    def resolve(self, url):
        def select_cb(resolved):
            stream_parts = []
            stream_parts_dict = {}

            for stream in resolved:
                if stream['surl'] not in stream_parts_dict:
                    stream_parts_dict[stream['surl']] = []
                    stream_parts.append(stream['surl'])
                stream_parts_dict[stream['surl']].append(stream)

            if len(stream_parts) == 1:
                dialog = xbmcgui.Dialog()
                quality = self.settings['quality'] or '0'
                resolved = resolver.filter_by_quality(stream_parts_dict[stream_parts[0]], quality)
                # if user requested something but 'ask me' or filtered result is exactly 1
                if len(resolved) == 1 or int(quality) > 0:
                    return resolved[0]
                opts = ['%s [%s]' % (r['title'], r['quality']) for r in resolved]
                ret = dialog.select(xbmcutil.__lang__(30005), opts)
                return resolved[ret]

            quality = self.settings['quality'] or '0'
            if quality == '0':
                dialog = xbmcgui.Dialog()
                opts = [__language__(30052),__language__(30053)]
                ret = dialog.select(xbmcutil.__lang__(30005), opts)
                if ret == 0:
                    return [stream_parts_dict[p][0] for p in stream_parts]
                elif ret == 1:
                    return [stream_parts_dict[p][-1] for p in stream_parts]
            else:
                return [stream_parts_dict[p][0] for p in stream_parts]

        item = self.provider.video_item()
        item.update({'url':url})
        return self.provider.resolve(item, select_cb=select_cb)

params = util.params()
if params == {}:
    xbmcutil.init_usage_reporting(__scriptid__)
MixerczXBMCContentProvider(mixercz.MixerczContentProvider(tmp_dir=xbmc.translatePath(__addon__.getAddonInfo('profile'))), settings, __addon__).run(params)
