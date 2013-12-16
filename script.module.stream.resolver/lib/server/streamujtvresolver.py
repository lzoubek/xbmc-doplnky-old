# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re,util

__name__='streamujtv'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def resolve(url):
    m = _regex(url)
    if m:
        data = util.request(url)
        streams = re.search('res0\:[^\"]*\"([^\"]+)',data,re.IGNORECASE|re.DOTALL)
        subs = re.search('sub0\:[^\"]*\"(http[^\"]+)',data,re.IGNORECASE|re.DOTALL)
        rn = re.search('rn\:[^\"]*\"([^\"]*)',data,re.IGNORECASE|re.DOTALL)
        if streams and rn:
            streams = streams.group(1).split(',')
            rn = rn.group(1).split(',')
            index = 0
            result = []
            for stream in streams:
                q = rn[index]
                if q == 'HD':
                    q = '720p'
                else:
                    q = '???'
                if subs:
                    result.append({'url':stream,'quality':q,'subs':subs.group(1)})
                else:
                    result.append({'url':stream,'quality':q})
                index+=1
            return result

def _regex(url):
    return re.search('streamuj\.tv/video/',url,re.IGNORECASE | re.DOTALL)

