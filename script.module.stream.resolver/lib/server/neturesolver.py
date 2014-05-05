# -*- coding: UTF-8 -*-
# *  GNU General Public License for more details.
# *
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *
# *  based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# */
import re, util, decimal, random, base64, urllib, urllib2

__name__ = 'netu'
def supports(url):
    return not _regex(url) == None

def _decode(data):
    def O1l(string):
        ret = ""
        i = len(string) - 1;
        while i>=0:
            ret+= string[i]
            i-=1
        return ret

    def l0I(data, ):
        enc = ""
        dec = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        i=0
        while True:
            h1 = dec.find(data[i]); i+=1;
            h2 = dec.find(data[i]); i+=1;
            h3 = dec.find(data[i]); i+=1;
            h4 = dec.find(data[i]); i+=1;
            bits = h1 << 18 | h2 << 12 | h3 << 6 | h4
            o1 = bits >> 16 & 0xff
            o2 = bits >> 8 & 0xff
            o3 = bits & 0xff
            if (h3 == 64):
                enc += unichr(o1)
            else:
                if (h4 == 64):
                    enc += unichr(o1)+ unichr(o2)
                else:
                    enc += unichr(o1)+ unichr(o2) + unichr(o3)
            if  (i >= len(data)):
                break
        return enc

    jsdec = l0I(O1l(data))
    escape= re.search("var _escape=\'([^\']+)", jsdec).group(1)
    return escape.replace('%','\\').decode('unicode-escape')

def _decode2(file_url):
    def K12K(a, typ='b'):
        codec_a = ["k", "3", "8", "N", "x", "c", "5", "R", "D", "G", "L", "9", "g", "6", "T", "w", "p", "b", "7", "4", "v", "B", "s", "t", "m", "="]
        codec_b = ["u", "I", "Z", "z", "n", "Q", "f", "U", "l", "a", "1", "J", "i", "2", "Y", "0", "e", "o", "H", "V", "W", "X", "d", "y", "M", "q"]
        if 'd' == typ:
            tmp = codec_a
            codec_a = codec_b
            codec_b = tmp
        idx = 0
        while idx < len(codec_a):
            a = a.replace(codec_a[idx], "___");
            a = a.replace(codec_b[idx], codec_a[idx]);
            a = a.replace("___", codec_b[idx]);
            idx += 1
        return a

    def _xc13(_arg1):
        _lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        _local2 = ""
        _local3 = [0, 0, 0, 0]
        _local4 = [0, 0, 0]
        _local5 = 0
        while _local5 < len(_arg1):
            _local6 = 0;
            while _local6 < 4 and (_local5 + _local6) < len(_arg1):
                _local3[_local6] = ( _lg27.find( _arg1[_local5 + _local6] ) )
                _local6 += 1;
            _local4[0] = ((_local3[0] << 2) + ((_local3[1] & 48) >> 4));
            _local4[1] = (((_local3[1] & 15) << 4) + ((_local3[2] & 60) >> 2));
            _local4[2] = (((_local3[2] & 3) << 6) + _local3[3]);

            _local7 = 0;
            while _local7 < len(_local4):
                if _local3[_local7 + 1] == 64:
                    break;
                _local2 += chr(_local4[_local7]);
                _local7 += 1;
            _local5 += 4;
        return _local2

    return _xc13(K12K(file_url, 'd'))


def resolve(url):
    m = _regex(url)
    if m:
        vid = m.group('vid')
        headers= {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0',
                            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        player_url = "http://netu.tv/player/embed_player.php?vid=%s&autoplay=no" % vid
        try:
            req = urllib2.Request(player_url, headers=headers)
            data = urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            if e.code == 404:
                data = e.fp.read()
        b64enc= re.search('base64([^\"]+)',data, re.DOTALL)
        b64dec = b64enc and base64.decodestring(b64enc.group(1))
        hash = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
        if hash:
            form = _decode(hash)
            data  = re.compile('<input name="([^"]+?)" [^>]+? value="([^"]+?)">').findall(form)
            post_data = {}
            for idx in range(len(data)):
                post_data[ data[idx][0] ] = data[idx][1]
            data = util.post(player_url, post_data, headers)
            b64enc= re.search('base64([^\"]+)',data, re.DOTALL)
            b64dec = b64enc and base64.decodestring(b64enc.group(1))
            hash = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
            if hash:
                file_vars_script = _decode(hash)
                file_vars = re.compile('var.+?= "([^"]*?)"').findall(file_vars_script)
                for file_var in file_vars:
                    file_url = _decode2(file_var)
                    if 'http' in file_url:
                        return [{'url':file_url,'quality':'???'}]

def _regex(url):
    m1 = m2 = m3 = None
    m1 = re.search("netu\.tv/watch_video\.php\?v=(?P<vid>[0-9A-Z]+)", url)
    m2 = re.search('netu\.tv/player/embed_player\.php\?vid=(?P<vid>[0-9A-Z]+)', url)
    b64enc= re.search('data:text/javascript\;charset\=utf\-8\;base64([^\"]+)',url)
    b64dec = b64enc and base64.decodestring(b64enc.group(1))
    hash = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
    if hash:
        form = _decode(hash)
        m3  = re.search('<input name="vid"[^>]+? value="(?P<vid>[^"]+?)">', form)
    return m1 or m2 or m3

