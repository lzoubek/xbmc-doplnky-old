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
import re,urllib,urllib2,cookielib,random,util,sys,os,traceback
import simplejson as json
from base64 import b64decode
from provider import ContentProvider
from provider import ResolveException
from provider import cached
class UloztoContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'ulozto.cz','http://www.ulozto.cz/',username,password,filter)
        self.search_type=''
        self.cp = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        self.rh = UloztoHTTPRedirectHandler()
        self.rh.throw = False
        self.rh.location = None
        self.init_urllib()

    def init_urllib(self):	
        opener = urllib2.build_opener(self.cp,self.rh)
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['login','search','resolve','categories']

    def categories(self):
        result = []
        if not self.login():
            return result
        data = util.request(self.base_url+'m/'+self.username)
        fav = re.search('<li id=\"fmFavoritesFolder.+?href=\"(?P<url>[^\"]+)[^>]*>(?P<title>[^<]+)',data,re.IGNORECASE|re.DOTALL)
        if fav:
            item = self.dir_item()
            item['url'] = '#fm#'+fav.group('url')
            item['title'] = fav.group('title')
            result.append(item)
        myfiles = re.search('<a class=\"fmHomeFolder.+?href=\"(?P<url>[^\"]+)[^>]*>(?P<title>[^<]+)',data,re.IGNORECASE|re.DOTALL)
        if myfiles:
            item = self.dir_item()
            item['url'] = '#fm#' + myfiles.group('url')
            item['title'] = myfiles.group('title')
            result.append(item)
        return result

    def search(self,keyword):
        return self.list(self.base_url+'hledej/?'+self.search_type+'q='+urllib.quote(keyword))

    def login(self):
        if self.username and self.password and len(self.username)>0 and len(self.password)>0:
            self.info('Login user=%s, pass=*****' % self.username)
            self.rh.throw = False
            page = util.request(self.base_url+'?do=web-login')
            if page.find('href="/?do=web-logout') > 0:
                self.info('Already logged in')
                return True
            data = util.substr(page,'<li class=\"menu-username','</li')
            m = re.search('key=(?P<key>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
            token = re.search('<input type=\"hidden\" name=\"_token_\".+?value=\"([^\"]+)"',page,re.IGNORECASE | re.DOTALL)
            if m and token:
                login_url = self.base_url+'login?key='+m.group('key')+'&do=loginForm-submit'
                data = util.post(login_url,{'username':self.username,'password':self.password,'remember':'on','login':'Prihlasit','_token_':token.group(1)})
                if data.find('href="/?do=web-logout') > 0:
                    self.info('Login successfull')
                    return True
            self.info('Login failed')
        return False

    def list_folder(self,url):
        self.login()
        result = []
        page = util.request(self._url(url))
        page = util.substr(page,'<div id=\"fmItems','</ul')
        for m in re.finditer('<div class=\"fmFolder(.+?)</em',page,re.IGNORECASE | re.DOTALL):
            data = m.group(1)
            item = self.dir_item()
            item['url'] = '#fm#' + re.search('data-href=\"([^\"]+)',data).group(1)
            item['title'] = re.search('data-name=\"([^\"]+)',data).group(1)
            item['img'] = re.search('<img src=\"([^\"]+)',data).group(1)
            result.append(item)
        for m in re.finditer('<div class=\"fmFile(.+?)</em>',page,re.IGNORECASE | re.DOTALL):
            data = m.group(1)
            item = self.video_item()
            item['url'] = re.search('data-href=\"([^\"]+)',data).group(1)
            item['title'] = '%s.%s' % (re.search('data-name=\"([^\"]+)',data).group(1),re.search('data-ext=\"([^\"]+)',data).group(1))
            item['img'] = re.search('<img src=\"([^\"]+)',data).group(1)
            result.append(item)
        return result

    @cached(1)
    def list(self,url):
        if url.find('#fm#') == 0:
            return self.list_folder(url[5:])
        url = self._url(url)
        page = util.request(url,headers={'X-Requested-With':'XMLHttpRequest','Referer':url,'Cookie':'uloz-to-id=1561277170;'})
        script = util.substr(page,'var kn','</script>')
        keymap = None
        key = None
        k = re.search('{([^\;]+)"',script,re.IGNORECASE | re.DOTALL)
        if k:
            keymap = json.loads("{"+k.group(1)+"\"}")
        j = re.search('kapp\(kn\[\"([^\"]+)"',script,re.IGNORECASE | re.DOTALL)
        if j:
            key = j.group(1)
        if not (j and k):
            self.error('error parsing page - unable to locate keys')
            return []
        burl = b64decode('I2h0dHA6Ly9jcnlwdG8uamV6em92by5uZXQvZGVjcnlwdC8/a2V5PSVzJnZhbHVlPSVzCg==')
        murl = b64decode('aHR0cDovL2NyeXB0by5qZXp6b3ZvLm5ldC9kZWNyeXB0Lwo=')
        data = util.substr(page,'<ul class=\"chessFiles','</ul>') 
        result = []
        req = {'seed':keymap[key],'values':keymap}
        decr = json.loads(util.post_json(murl,req))
        for li in re.finditer('<li data-icon=\"(?P<key>[^\"]+)',data, re.IGNORECASE |  re.DOTALL):
            body = urllib.unquote(b64decode(decr[li.group('key')]))
            m = re.search('<li>.+?<div data-icon=\"(?P<key>[^\"]+)[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)<div class=\"fileInfo(?P<info>.+?)</h4>',body, re.IGNORECASE |  re.DOTALL)
            if not m:
                continue
            value = keymap[m.group('key')]
            info = m.group('info')
            iurl = burl % (keymap[key],value)
            item = self.video_item()
            item['title'] = '.. title not found..'
            title = re.search('<div class=\"fileName.+?<a[^>]+>(?P<title>[^<]+)',info, re.IGNORECASE|re.DOTALL)
            if title:
                item['title'] = title.group('title')
            size = re.search('<span class=\"fileSize[^>]+>(?P<size>[^<]+)',info, re.IGNORECASE|re.DOTALL)
            if size:
                item['size'] = size.group('size').strip()
            time = re.search('<span class=\"fileTime[^>]+>(?P<time>[^<]+)',info, re.IGNORECASE|re.DOTALL)
            if time:
                item['length'] = time.group('time')
            item['url'] = iurl
            item['img'] = m.group('logo')
            self._filter(result,item)
        # page navigation
        data = util.substr(page,'<div class=\"paginator','</div')
        mnext = re.search('<a href=\"(?P<url>[^\"]+)\" class="next',data)
        if mnext:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = mnext.group('url')
            result.append(item)
        return result

    @cached(48)
    def decr_url(self,url):
        if url.startswith('#'):
            ret = json.loads(util.request(url[1:]))
            if ret.has_key('result'):
                url = b64decode(ret['result'])
                url = self._url(url)
        return url

    def resolve(self,item,captcha_cb=None):
        item = item.copy()
        url = item['url']
        if url.startswith('http://www.ulozto.sk'):
            url = self.base_url + url[20:]
        url = self.decr_url(url)
        url = self._url(url)
        if url.startswith('#'):
            util.error('[uloz.to] - url was not correctly decoded')
            return
        self.init_urllib()
        self.login()
        self.info('Resolving %s'% url)
        if not item.has_key('vip'):
            item['vip'] = False
        vip = item['vip']
        if vip:
            page = util.request(url)
        else:
            try:
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                page = response.read()
                response.close()
            except urllib2.HTTPError, e:
                traceback.print_exc()
                return
        if page.find('Stránka nenalezena!') > 0:
            self.error('page with movie was not found on server')
            return

        if vip:
            data = util.substr(page,'<h3>Neomezené stahování</h3>','</div')
            m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
            if m:
                try:
                    self.rh.throw = True
                    resp = urllib2.urlopen(urllib2.Request(self._url(m.group('url'))))
                except RedirectionException:
                    # this is what we need, our redirect handler raises this
                    pass
                except urllib2.HTTPError:
                    # this is not OK, something went wrong
                    traceback.print_exc()
                    self.error('Cannot resolve stream url, server did not redirected us')
                    self.info('POST url:'+post_url)
                    return
                stream = self.rh.location
                item['url'] = self._fix_stream_url(stream)
                item['surl'] = url
                return item

        else:
            data = util.substr(page,'<h3>Omezené stahování</h3>','<script')
            m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"',data,re.IGNORECASE | re.DOTALL)
            if m:
                self.rh.throw = True
                stream_url = self._get_file_url_anonymous(page,self._url(m.group('action')),response.headers,captcha_cb)
                if stream_url:
                    item['url'] = stream_url
                    item['surl'] = url
                    return item

    def _get_file_url_anonymous(self,page,post_url,headers,captcha_cb):

        capdata = json.loads(util.request(self._url('reloadXapca.php')))
        captcha = capdata['image']
        # ask callback to provide captcha code
        self.info('Asking for captcha img %s' % captcha)
        code = captcha_cb({'id':captcha,'img': captcha})
        if not code:
            self.info('Captcha not provided, done')
            return

        ts = re.search('<input type=\"hidden\" name=\"ts\".+?value=\"([^\"]+)"',page,re.IGNORECASE | re.DOTALL)
        cid = re.search('<input type=\"hidden\" name=\"cid\".+?value=\"([^\"]+)"',page,re.IGNORECASE | re.DOTALL)
        sign = re.search('<input type=\"hidden\" name=\"sign\".+?value=\"([^\"]+)"',page,re.IGNORECASE | re.DOTALL)
        has = capdata['hash']
        salt = capdata['salt']
        timestamp = capdata['timestamp']
        token = re.search('<input type=\"hidden\" name=\"_token_\".+?value=\"([^\"]+)"',page,re.IGNORECASE | re.DOTALL)
        if not (sign and ts and cid and has and token):
            util.error('[uloz.to] - unable to parse required params from page, plugin needs fix')
            return
        request = urllib.urlencode({'hash':has,'salt':salt,'timestamp':timestamp,'ts':ts.group(1),'cid':cid.group(1),'sign':sign.group(1),'captcha_value':code,'freeDownload':'Stáhnout','_token_':token.group(1)})
        req = urllib2.Request(post_url,request)
        req.add_header('User-Agent',util.UA)
        req.add_header('Referer',post_url)
        req.add_header('Accept','application/json')
        req.add_header('X-Requested-With','XMLHttpRequest')
        sessid=[]
        for cookie in re.finditer('(ULOSESSID=[^\;]+)',headers.get('Set-Cookie'),re.IGNORECASE | re.DOTALL):
            sessid.append(cookie.group(1))
        req.add_header('Cookie','nomobile=1; uloztoid='+cid.group(1)+'uloztoid2='+cid.group(1)+'; '+sessid[-1])
        try:
            resp = urllib2.urlopen(req)
            page = resp.read()
            headers = resp.headers
        except urllib2.HTTPError:
            # this is not OK, something went wrong
            traceback.print_exc()
            util.error('[uloz.to] cannot resolve stream url, server did not redirected us')
            util.info('[uloz.to] POST url:'+post_url)
            return
        try:
            result = json.loads(page)
        except:
            raise ResolveException('Unexpected error, addon needs fix')
        if result['status'] == 'ok':
            return self._fix_stream_url(result['url'])
        elif result['status'] == 'error':
            # the only known state is wrong captcha for now
            util.error('Captcha validation failed, please try playing/downloading again')
            util.error(result)
            raise ResolveException('Captcha failed, try again')


    def _fix_stream_url(self,stream):	
        index = stream.rfind('/')
        if index > 0:
            fn = stream[index:]
            index2 = fn.find('?')
            if index2 > 0:
                fn = urllib.quote(fn[:index2])+fn[index2:]
            else:
                fn = urllib.quote(fn)
            stream = stream[:index]+fn
        return stream



def _regex(url):
    return re.search('(#(.*)|ulozto\.cz|uloz\.to)',url,re.IGNORECASE | re.DOTALL)

class UloztoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        if self.throw:
            self.location = headers.getheader('Location')
            raise RedirectionException()
        else:
            return urllib2.HTTPRedirectHandler.http_error_302(self,req,fp,code,msg,headers)

class RedirectionException(Exception):
    pass

