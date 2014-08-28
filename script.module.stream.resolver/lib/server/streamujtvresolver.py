# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re,util
import simplejson as json
from base64 import b64decode, b64encode

__name__='streamujtv'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def resolve(url):
    m = _regex(url)
    if m:
        data = util.request(url)
        if data.find('Toto video neexistuje') > 0:
            util.error('Video bylo smazano ze serveru')
            return
        player = 'http://www.streamuj.tv/new-flash-player/mplugin4.swf'
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
                    'Referer':'http://www.streamuj.tv/mediaplayer/player.swf'}
        burl = b64decode('aHR0cDovL2Z1LWNlY2gucmhjbG91ZC5jb20vcGF1dGg=')
        index = 0
        result = []
        qualities = re.search('rn\:[^\"]*\"([^\"]*)',data,re.IGNORECASE|re.DOTALL)
        langs = re.search('langs\:[^\"]*\"([^\"]+)',data,re.IGNORECASE|re.DOTALL)
        for lang in langs.group(1).split(','):
            streams = re.search('res'+str(index)+'\:[^\"]*\"([^\"]+)',data,re.IGNORECASE|re.DOTALL)
            subs = re.search('sub'+str(index)+'\:[^\"]*\"([^\"]+)',data,re.IGNORECASE|re.DOTALL)
            if subs: 
                subs = re.search('[^>]+>([^$]+)',subs.group(1),re.IGNORECASE|re.DOTALL)
            if streams and qualities:
                streams = streams.group(1).split(',')
                rn = qualities.group(1).split(',')
                qindex = 0
                for stream in streams:
                    res = json.loads(util.post_json(burl,{'link':stream,'player':player}))
                    stream = res['link']
                    q = rn[qindex]
                    if q == 'HD':
                        q = '720p'
                    else:
                        q = 'SD'
                    l = ' '+lang
                    if subs:
                        l += ' + subs'
                        s = subs.group(1)
                        s = json.loads(util.post_json(burl,{'link':s,'player':player}))
                        result.append({'url':stream,'quality':q,'subs':s['link'],'headers':headers,'lang':l})
                    else:
                        result.append({'url':stream,'quality':q,'headers':headers, 'lang':l})
                    qindex+=1
            index+=1
        return result

def _regex(url):
    return re.search('streamuj\.tv/video/',url,re.IGNORECASE | re.DOTALL)

