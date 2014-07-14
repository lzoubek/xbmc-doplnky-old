from xbmcswift2 import Plugin
from xbmcswift2 import xbmc
from xbmcswift2 import xbmcaddon
from resources.lib.api import Nekonecne

plugin = Plugin()
__addon__ = xbmcaddon.Addon()
__useremail__ = __addon__.getSetting('useremail')
__password__ = __addon__.getSetting('password')

api = Nekonecne(__useremail__, __password__)

@plugin.route('/channel/<url>/')
def play_stream(url):
    stream = api.get_stream(url)
    if stream < 0:
        plugin.log.info('Failed to get correct stream')
        return -1
    plugin.log.info('Playing url: %s' % stream)
    plugin.set_resolved_url(stream) 

@plugin.route('/')
def channels():
    result = api.check_settings()
    if result < 0:
        msg = 'Invalid settings. Please check add-on settings!'
        plugin.log.info(msg)
        return [{'label': msg}]
        
    result = api.is_cookie_valid()
    if result < 0:
        msg = 'Cookie is invalid! Please verify add-on settings!'
        plugin.log.info(msg)
        return [{'label': msg}]
    
    channels = api.get_channels()
    if len(channels) < 1:
        msg = 'Failed to get channellist'
        plugin.log.info(msg)
        return [{'label': msg}]

    items = [{
        'label': channel['name'],
        'path': plugin.url_for('play_stream', url=channel['url']),
        'thumbnail': channel['logo'],
        'is_playable': True
    } for channel in channels]

    return items

if __name__ == '__main__':
    plugin.run()
