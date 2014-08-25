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
        streams = re.search('res0\:[^\"]*\"([^\"]+)',data,re.IGNORECASE|re.DOTALL)
        subs = re.search('sub0\:[^>]+>(http[^\"]+)',data,re.IGNORECASE|re.DOTALL)
        rn = re.search('rn\:[^\"]*\"([^\"]*)',data,re.IGNORECASE|re.DOTALL)
        if data.find('Toto video neexistuje') > 0:
            util.error('Video bylo smazano ze serveru')
            return
        if streams and rn:
            streams = streams.group(1).split(',')
            rn = rn.group(1).split(',')
            index = 0
            result = []
            player = 'http://www.streamuj.tv/new-flash-player/mplugin4.swf'
            headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
                    'Referer':'http://www.streamuj.tv/mediaplayer/player.swf'}
            for stream in streams:
                burl = b64decode('aHR0cDovL2Z1LWNlY2gucmhjbG91ZC5jb20vcGF1dGg=')
                res = json.loads(util.post_json(burl,{'link':stream,'player':player}))
                stream = res['link']
                q = rn[index]
                if q == 'HD':
                    q = '720p'
                else:
                    q = '???'
                if subs:
                    s = subs.group(1).replace('&','%26')
                    s = json.loads(util.post_json(burl,{'link':s,'player':player}))
                    result.append({'url':stream,'quality':q,'subs':s['link'],'headers':headers})
                else:
                    result.append({'url':stream,'quality':q,'headers':headers})
                index+=1
            return result

def _regex(url):
    return re.search('streamuj\.tv/video/',url,re.IGNORECASE | re.DOTALL)

