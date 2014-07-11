import cookielib, urllib, urllib2
import urlparse
import CommonFunctions

BASE_URL = 'http://flash.nekonecne.cz'
APPEND_LOGINURL = '/user.php'

FIELD_USEREMAIL = 'Pnick'
FIELD_HESLO = 'Ppass'

COOKIEID_USEREMAIL = 'coomail'
COOKIEID_HESLO = 'cooheslo'

STREAMID = 'Playlist vlc'

common = CommonFunctions
cj = cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

def _url(base, path):
    return urlparse.urljoin(base, path)

def _urlnetloc(url):
    parts = urlparse.urlparse(url)
    if parts.netloc == '':
        return -1
    return ('http://' + parts.netloc)

def get(url):
    '''Performs a GET request for the given url and returns the response'''
#    opener.addheaders.append(('Referer', referer))
    try:
        sock = opener.open(url)
    except ValueError:
        return -1
    if sock.getcode() != 200:
        sock.close()
        return -2
    resp = sock.read()
    sock.close()
    return resp

def post(url, params):
    '''Performs a POST request for the given url and returns the response'''
    try:
        sock = opener.open(url, params)
    except ValueError:
        return -1
    if sock.getcode() != 200:
        sock.close()
        return -2
    resp = sock.read()
    sock.close()
    return resp

def check_settings(usermail, password):
    if usermail is '' or password is '':
        return -1
    return 0

def check_cookie(url, useremail, password):
    params = urllib.urlencode({FIELD_USEREMAIL: useremail,
                                FIELD_HESLO: password})
    html = post(url, params)
    cookie_email = get_cookie_by_name(COOKIEID_USEREMAIL)
    cookie_heslo = get_cookie_by_name(COOKIEID_HESLO)    
    if not cookie_email or not cookie_heslo:
        return -1
    return 0

def get_redirect_url():
    html = get(BASE_URL)
    parsed = common.parseDOM(html, 'meta', attrs={'http-equiv': 'refresh'}, ret='url')
    if len(parsed) < 1:
        return -1
    return _urlnetloc(common.makeAscii(parsed[0]))

def get_login_url():
    baseurl = get_redirect_url()
    return _url(baseurl, APPEND_LOGINURL)

def get_cookie_by_name(name):
    for cookie in cj:
        if cookie.name == name:
            return cookie.value
    return -1

def get_channels(url):
    baseurl = _urlnetloc(url)
    html = get(url)
    parsed = common.parseDOM(html, 'div', attrs={'class': 'list'})
    if len(parsed) < 1:
        return -1
    parsed = common.parseDOM(parsed, 'div', attrs={'class': 'item'})
    items = []
    for channel in parsed:
        link = common.parseDOM(channel, 'a', ret='href')
        name = common.parseDOM(channel, 'img')
        logo = common.parseDOM(channel, 'img', ret='src')

        # Assemble full URL
        link = common.makeAscii(link)
        link = _url(baseurl, link)

        # Clean those
        logo = common.makeAscii(logo)
        name = common.makeAscii(name)
        name = common.stripTags(name)
        
        items.append({
            'name': name,
            'url': link,
            'logo' : logo
        })       
    return items
        
def get_stream(url):
    html = get(url)
    parsed = common.parseDOM(html, 'div', attrs={'class': 'player'})
    if len(parsed) < 1:
        return -1
    identifiers = common.parseDOM(parsed, 'a', attrs={'target': '_blank'})
    identifiers = common.parseDOM(identifiers, 'img', ret='alt')
    urls = common.parseDOM(parsed, 'a', attrs={'target': '_blank'}, ret='href')

    if(len(urls) != len(identifiers)):
        return -2
    num = 0
    for ident in identifiers:
        if ident == STREAMID:
            resolved_url = urls[num]
        num += 1
    if resolved_url == '':
        return -3
    return resolved_url
