# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re,util
__name__='nahnoji'
def supports(url):
	return not _regex(url) == None

# returns the steam url
def url(url):
	if supports(url):
		if url.find('.flv') > -1:
			return url
		data = util.substr(util.request(url),'<body style','</a>')
		pattern = 'href=\"(.+?)\"[^>]+>' 
		match = re.compile(pattern).findall(data)
		
		return [match[0]]

def _regex(url):
	return re.search('nahnoji.cz/(.+?)',url,re.IGNORECASE | re.DOTALL)
