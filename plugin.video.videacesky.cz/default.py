# -*- coding: UTF-8 -*-
# /*
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
import os
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, util, xbmcprovider, xbmcutil, resolver
from provider import ResolveException

__scriptid__ = 'plugin.video.videacesky.cz'
__scriptname__ = 'videacesky.cz'
__addon__ = xbmcaddon.Addon(id=__scriptid__)
__language__ = __addon__.getLocalizedString
__settings__ = __addon__.getSetting

sys.path.append(os.path.join (__addon__.getAddonInfo('path'), 'resources', 'lib'))
import videacesky
settings = {'downloads':__addon__.getSetting('downloads'), 'quality':__addon__.getSetting('quality')}


def vp8_youtube_filter(stream):
	# some embedded devices running xbmc doesnt have vp8 support, so we
	# provide filtering ability for youtube videos
	
	#======================================================================
	# 	  5: "240p h263 flv container",
	#      18: "360p h264 mp4 container | 270 for rtmpe?",
	#      22: "720p h264 mp4 container",
	#      26: "???",
	#      33: "???",
	#      34: "360p h264 flv container",
	#      35: "480p h264 flv container",
	#      37: "1080p h264 mp4 container",
	#      38: "720p vp8 webm container",
	#      43: "360p h264 flv container",
	#      44: "480p vp8 webm container",
	#      45: "720p vp8 webm container",
	#      46: "520p vp8 webm stereo",
	#      59: "480 for rtmpe",
	#      78: "seems to be around 400 for rtmpe",
	#      82: "360p h264 stereo",
	#      83: "240p h264 stereo",
	#      84: "720p h264 stereo",
	#      85: "520p h264 stereo",
	#      100: "360p vp8 webm stereo",
	#      101: "480p vp8 webm stereo",
	#      102: "720p vp8 webm stereo",
	#      120: "hd720",
	#      121: "hd1080"
	#======================================================================
	try:
		if stream['fmt'] in [38, 44, 45, 46, 100, 101, 102]:
			return True
	except KeyError:
		return False
	return False


class VideaceskyXBMCContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):
	
    def play(self, url):
        stream = self.resolve(url)
        print type(stream)
        if type(stream) == type([]):
            # resolved to mutliple files, we'll feed playlist and play the first one
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            for video in stream:
                li = xbmcgui.ListItem(label=video['title'], path=video['url'], iconImage='DefaultVideo.png')
                playlist.add(video['url'], li)
            stream = stream[0]
        if stream:
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
                if __settings__('filter_vp8') and vp8_youtube_filter(stream):
                    continue
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
           
            dialog = xbmcgui.Dialog()
            opts = [__language__(30059)]
            # when there are multiple stream, we let user choose only from best qualities
            opts = opts + ['%s [%s]' % (stream_parts_dict[p][0]['title'], stream_parts_dict[p][0]['quality']) for p in stream_parts]
            ret = dialog.select(xbmcutil.__lang__(30005), opts)
            if ret == 0:
                # requested to play all streams in given order - so return them all
                return [stream_parts_dict[p][0] for p in stream_parts]
            if ret >= 0:
               return stream_parts_dict[stream_parts[ret]][0]

        item = self.provider.video_item()
        item.update({'url':url})
        try:
            return self.provider.resolve(item, select_cb=select_cb)
        except ResolveException, e:
            self._handle_exc(e)

params = util.params()
if params == {}:
	xbmcutil.init_usage_reporting(__scriptid__)
VideaceskyXBMCContentProvider(videacesky.VideaceskyContentProvider(tmp_dir=xbmc.translatePath(__addon__.getAddonInfo('profile'))), settings, __addon__).run(params)

