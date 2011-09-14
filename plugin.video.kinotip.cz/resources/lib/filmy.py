import xbmc,xbmcplugin,re,sys,urllib2,xbmcgui,random

SERVER='filmy'
BASE_URL='http://filmy.kinotip.cz/'

def request(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()
	return data

def substr(data,start,end):
	i1 = data.find(start)
	i2 = data.find(end,i1)
	return data[i1:i2]
		
def add_dir(name,id,logo=''):
	if not logo == '':
		if logo.find('/') == 0:
			logo = logo[1:]
		if logo.find('http://') < 0:
			logo = BASE_URL+logo
     	u=sys.argv[0]+"?server="+SERVER+"&"+id
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=logo)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def add_stream(name,url,logo):
	url=sys.argv[0]+"?server="+SERVER+"&play="+url
	li=xbmcgui.ListItem(name,path = url,iconImage="DefaultVideo.png",thumbnailImage=logo)
        li.setInfo( type="Video", infoLabels={ "Title": name} )
	li.setProperty("IsPlayable","true")
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li,isFolder=False)

def root():
	add_dir('Kategorie filmů','list=categories','')
	add_dir('Filmy podle herců','list=artists','')
	add_dir('Filmy podle roku','list=years','')
	add_dir('Vyhledat','search=string','')


def listing(param):
	data = request(BASE_URL)
	if 'categories' == param:
		return listing_categories(data)
	if 'artists' == param:
		return listing_artists(data)
	if 'years' == param:
		return listing_years(data)

def listing_categories(data):
	pattern='<li[^>]+><a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, substr(data,'<h2>Kategorie filmů</h2>','</ul>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),'cat='+m.group('link'),'')

def listing_artists(data):
	pattern='<a href=\'(?P<link>[^\']+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, substr(data,'<h2>Filmy podle herců</h2>','</li>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),'cat='+m.group('link'),'')

def listing_years(data):
	print substr(data,'<h2>Filmy podle roku</h2>','</ul>')
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, substr(data,'<h2>Filmy podle roku</h2>','</ul>'), re.IGNORECASE | re.DOTALL):
		add_dir(m.group('cat'),'cat='+m.group('link'),'')
def search():
	kb = xbmc.Keyboard('','Vyhledat',False)
	kb.doModal()
	if kb.isConfirmed():
		data = request(BASE_URL+'?s='+kb.getText())
		return list_movies(data)

def list_movies(data):
	pattern = '<div class=\"post\"(.+?)<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(.+?)<img(.+?)src=\"(?P<img>[^\"]+)'
	for m in re.finditer(pattern,substr(data,'<div class=\"content\"','<div class=\"sidebar\"'),re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'),'movie='+m.group('url'),m.group('img'))
	
	data = substr(data,'<div id=\'wp_page_numbers\'>','</div>')
	k = re.search('<li class=\"page_info\">(?P<page>(.+?))</li>',data,re.IGNORECASE | re.DOTALL)
	if not k == None:
		n = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>\&lt;</a>',data,re.IGNORECASE | re.DOTALL)
		if not n == None:
			add_dir(k.group('page')+' - jít na předchozí','cat='+n.group('url'),'')
		m = re.search('<a href=\"(?P<url>[^\"]+)[^>]+>\&gt;</a>',data,re.IGNORECASE | re.DOTALL)
		if not m == None:
			add_dir(k.group('page')+' - jít na další','cat='+m.group('url'),'')

def _server_name(url):
	return re.search('http\://([^/]+)',url,re.IGNORECASE | re.DOTALL).group(1)

def movie(data):
	print 'listing movie'
	data = substr(data,'<div class=\"content\"','<div class=\"sidebar\"')
	pattern = '<embed src=\"(?P<embed>[^\"]+)(.+?)</p>'
	source = 1
	for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL):
		add_stream('Zdroj %d - %s' % (source,_server_name(m.group('embed'))),m.group('embed'),'')
		source += 1

def play(url):
	print 'Resolving '+url
	for stream in resolve_stream(url):
		print 'Sending %s to player' % stream
		li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
def resolve_stream(url):
	for f in [_videobb]:
		yield f(url)

def _videobb(url):
	if not re.search('http://(www\.)?videobb.com', url, re.IGNORECASE | re.DOTALL) == None:
		id = re.sub("http://(www\.)?videobb.com/e/",'',url)
		return "http://s%d.videobb.com/s?v=%s&r=1&t=%d&u=&c=12&start=0" % (random.randint(1,35),id,random.randint(1000000000,9999999999))

def handle(params):
	if len(params)==1:
		root()
	if 'list' in params.keys():
		listing(params['list'])
	if 'search' in params.keys():
		search()
	if 'cat' in params.keys():
		list_movies(request(params['cat']))
	if 'movie' in params.keys():
		movie(request(params['movie']))
	if 'play' in params.keys():
		return play(params['play'])
	return xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
