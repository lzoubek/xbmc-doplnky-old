# *      Copyright (C) 2011 Libor Zoubek
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

import sys,os,util,re,traceback

# dummy implementation of 2nd generation of resolving
# this will be injected to each resolver, that does not have this method yet
def _resolve(link):
    resolved = []
    streams = resolve(link)
    if streams == None:
        return None
    for stream in streams:
        item = {}
        item['name'] = stream
        item['url'] = stream
        item['quality'] = '???'
        item['surl'] = link
        item['subs'] = ''
        resolved.append(item)
    return resolved

sys.path.append( os.path.join ( os.path.dirname(__file__),'server') )

RESOLVERS = []
util.debug('%s searching for modules' % __name__)
for module in os.listdir(os.path.join(os.path.dirname(__file__),'server')):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    module = module[:-3]
    exec 'import %s' % module
    resolver = eval(module)
    util.debug('found %s %s' % (resolver,dir(resolver)))
    if not hasattr(resolver,'resolve'):
        resolver.resolve = _resolve
    RESOLVERS.append(resolver)
del module
util.debug('done')


##
# resolves given URL to list of streams 
# @param url
# @return [] iff resolver was found but failed
# @return None iff no resolver was found
# @return array of stream URL's 
def resolve(url):
    url = util.decode_html(url)
    util.info('Resolving '+url)
    resolver = _get_resolver(url)
    if resolver == None:
        return None
    value = resolver.url(url)
    if value == None:
        return []
    return value

def resolve2(url):
    url = util.decode_html(url)
    util.info('Resolving '+url)
    resolver = _get_resolver(url)
    value = None
    if resolver == None:
        return None
    util.debug('Using resolver '+str(resolver.__name__));
    try:
        value = resolver.resolve(url)
    except:
        traceback.print_exc()
    if value == None:
        return []
    def fix_key(i):
        if not 'subs' in i.keys():
            i['subs'] = ''
    [fix_key(i) for i in value]
    return sorted(value,key=lambda i:i['quality'])


def _get_resolver(url):
    util.debug('Get resolver for '+url)
    for r in RESOLVERS:
        util.debug('querying %s' % r)
        if r.supports(url):
            return r

# returns true iff we are able to resolve stream by given URL
def can_resolve(url):
    return not _get_resolver(url) == None
##
# finds streams in given data according to given regexes
# respects caller addon's setting about quality, asks user if needed
# @param data piece of text (HTML code) to search in
# @param regexes - array of strings - regular expressions, each MUST define named group called 'url'
#        which retrieves resolvable URL (that one is passsed to resolve operation)
# @return exactly 1 dictionary with keys: name,url,quality,surl
# @return None if at least 1 resoler failed to resolve and nothing else has been found
# @return [] if no resolvable URLs or no resolvers for URL has been found
def findstreams(data,regexes):
    resolvables = {}
    resolved = []
    # keep list of found urls to aviod having duplicates
    urls = []
    error = False
    for regex in regexes:
        for match in re.finditer(regex,data,re.IGNORECASE | re.DOTALL):
            util.info('Found resolvable %s ' % match.group('url'))
            resolvables[match.group('url')] = None
    for rurl in resolvables:        
            streams = resolve2(rurl)
            if streams == []:
                util.debug('There was an error resolving '+rurl)
                error = True
            if not streams == None:
                if len(streams) > 0:
                    for stream in streams:
                        resolved.append(stream)
    if error and len(resolved) == 0:
        return None
    if len(resolved) == 0:
        return {}
    resolved = sorted(resolved,key=lambda i:i['quality'])
    resolved = sorted(resolved,key=lambda i:len(i['quality']))
    resolved.reverse()
    return resolved

q_map = {'3':'720p','4':'480p','5':'360p'}

def filter_by_quality(resolved,q):
    util.info('filtering by quality setting '+q)
    if q == '0':
        return resolved
    sources = {}
    ret = []
    for item in resolved:
        if item['surl'] in sources.keys():
            sources[item['surl']].append(item)
        else:
            sources[item['surl']] = [item]
    if q == '1':
        # always return best quality from each source
        for key in sources.keys():
            ret.append(sources[key][-1])
    elif q == '2':
        #always return worse quality from each source
        for key in sources.keys():
            ret.append(sources[key][0])
    else:
        quality = q_map[q]
        # 3,4,5 are 720,480,360
        for key in sources.keys():
            added = False
            for item in sources[key]:
                if quality == item['quality']:
                    ret.append(item)
                    added = True
            if not added:
                util.debug('Desired quality %s not found, adding best found'%quality)
                ret.append(sources[key][-1])
    return ret


##
# finds streams in given data according to given regexes
# respects caller addon's setting about desired quality, asks user if needed
# assumes, that all resolvables need to be returned, but in particular quality
# @param data piece of text (HTML code) to search in
# @param regexes - array of strings - regular expressions, each MUST define named group called 'url'
#        which retrieves resolvable URL (that one is passsed to resolve operation)
# @return array of dictionaries with keys: name,url,quality,surl
# @return None if at least 1 resoler failed to resolve and nothing else has been found
# @return [] if no resolvable URLs or no resolvers for URL has been found
def findstreams_multi(data,regexes):
    resolved = []
    # keep list of found urls to aviod having duplicates
    urls = []
    error = False
    for regex in regexes:
        for match in re.finditer(regex,data,re.IGNORECASE | re.DOTALL):
            print 'Found resolvable %s ' % match.group('url')
            streams = resolve2(match.group('url'))
            if streams == []:
                util.debug('There was an error resolving '+match.group('url'))
                error = True
            if not streams == None:
                if len(streams) > 0:
                    for stream in streams:
                        resolved.append(stream)
    if error and len(resolved) == 0:
        return None
    if len(resolved) == 0:
        return []
    resolved = sorted(resolved,key=lambda i:i['quality'])
    resolved = sorted(resolved,key=lambda i:len(i['quality']))
    resolved2 = resolved
    resolved2.reverse()
    qualities = {}
    for item in resolved2:
        if item['quality'] in qualities.keys():
            qualities[item['quality']].append(item)
        else:
            qualities[item['quality']] = [item]
    # now .. we must sort items to be in same order as they were found on page
    for q in qualities.keys():
        qualities[q] = sorted(qualities[q],key=lambda i:resolved.index(i))
    return qualities
