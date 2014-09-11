# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2014 Maros Ondrasek
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

import calendar
import cookielib
import itertools
import re
import urllib
import urllib2
import mimetools
import mimetypes
from datetime import date

import util
from provider import ContentProvider

SPRAVODAJSTVO_URL = 'http://www.ta3.com/archiv.html'
SPRAVODAJSTVO_START = '<select name="category" id="articleArchivFilterSpravodajstvo-category">'
SPRAVODAJSTVO_END = '</select>'
SPRAVODAJSTVO_ITER_RE = r'<option\ value=\"(?P<id>\d+)\">(?P<title>[^<]+)</option>'

PUBLICISTIKA_URL = 'http://www.ta3.com/archiv/publicistika.html'
PUBLICISTIKA_START = '<select name="category" id="articleArchivFilterPublicistika-category">'
PUBLICISTIKA_END = '</select>'
PUBLICISTIKA_ITER_RE = r'<option\ value=\"(?P<id>\d+)\">(?P<title>[^<]+)</option>'

TLACOVE_BESEDY_URL = 'http://www.ta3.com/archiv/tlacove-besedy.html'
ONLINE_ROZHOVORY_URL = 'http://www.ta3.com/archiv/online-rozhovory.html'

TOP_START = '<div id="most-articles" class="widget">'
TOP_START_6HOURS = 'id="most-m6h"'
TOP_START_DAY = 'id="most-m1d"'
TOP_START_WEEK = 'id="most-m7d"'
TOP_END_6HOURS = TOP_START_DAY
TOP_END_DAY = TOP_START_WEEK
TOP_END = '<div class="widget program-widget" id="program">'
TOP_END_WEEK = TOP_END
TOP_ITER_RE = r"""
    <li>\s+
        <a\ href=\"(?P<url>[^\"]+)\"><span\ class=\"video\">[^<]+</span>(?P<title>[^<]+)</a>\s+
        <span\ class=\"tw\">\s+
            \((?P<views>\d+)\)\s+
        </span>\s+
    </li>
"""
LISTING_START = '<div class="inside archive-filter">'
LISTING_END = '<div id="right-column">'
LISTING_ITER_RE = r"""
    <li[^>]*>\s+
        <span\ class=\"time\">(?P<date>[^<]+)</span>\s+
        <a\ href=\"(?P<url>[^\"]+)\"><span\ class="vicon"></span>(?P<title>[^<]+)</a>\s+
    </li>
"""
PAGER_START = '<div class="paginator">'
PAGER_END = '</div>'
PAGER_ITER_RE = r"""
    <li(\s*class=\"(?P<type>[^\"]+)\")?>\s+
        <a\ href=\"(?P<url>[^\"]+)\">(\s+
            <span\ class=\"text\">(?P<title>[^<]+)</span>)?
        [^<]+</a>\s+
    </li>
"""

VIDEOTYPE_START = 'arrTa3VideoPlayer.push'
VIDEOTYPE_END=  ';'
VIDEOTYPE_RE = r'"(?P<id>[A-Z,0-9,\-]+)\"[^\"]+\"(?P<type>\d+)"'

PLAYER_ONLINE_URL = 'http://embed.livebox.cz/ta3/player-live.js'
PLAYER_OFFLINE_URL = 'http://embed.livebox.cz/ta3/player-offline.js'

VIDEO_FLASHVARS_RE = r'flashvars = \{(?P<flashvars>[^\}]+)\}'
VIDEO_LIVE_LOW_RE = r'videoID1:[^\']+\'(?P<low_id>[^\']+)'
VIDEO_LIVE_MEDIUM_RE = r'videoID2:[^\']+\'(?P<medium_id>[^\']+)'
VIDEO_LIVE_HIGH_RE = r'videoID3:[^\']+\'(?P<high_id>[^\']+)'
VIDEO_PREFIX_RE = r'prefix:[^\']+\'(?P<prefix>[^\']+)'
VIDEO_POSTFIX_RE = r'postfix:[^\']+\'(?P<postfix>[^\']+)'

VIDEOTEKA_TYPE = {'undefined':'Videoteka/mp4:', '0':'Videoteka/mp4:', '1':'VideotekaEncoder/mp4:'}
QUALITY_POSTFIX = {"576p":"_ta1d.mp4", "404p":"_ta2d.mp4", "288p":"_ta3d.mp4"}


class TA3ContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, 'ta3.com', 'http://www.ta3.com/', username, password, filter, tmp_dir)
        self.cp = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        self.rh = TA3HTTPRedirectHandler()
        self.init_urllib()

    def init_urllib(self):
        opener = urllib2.build_opener(self.cp,self.rh)
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['categories', 'resolve', '!download']

    def list(self, url):
        if not url.startswith('#'):
            params = ""
        else:
            params = url[:url.rfind('#')] + '#'
        if url.find('#top#') == 0:
            return self.list_top(util.request(SPRAVODAJSTVO_URL))
        if url.find('#top6h#') == 0:
            return self.list_top_6hours(util.request(SPRAVODAJSTVO_URL))
        if url.find('#top1d#') == 0:
            return self.list_top_day(util.request(SPRAVODAJSTVO_URL))
        if url.find('#top1w#') == 0:
            return self.list_top_week(util.request(SPRAVODAJSTVO_URL))
        if url.find('#catsp#') == 0:
            return self.list_spravodajstvo_categories()
        if url.find('#catpb#') == 0:
            return self.list_publicistika_categories()
        if url.find("#date#") == 0:
            year = int(url.split("#")[2])
            month = int(url.split("#")[3])
            url = url.split("#")[-1]
            return self.date(year, month, url)
        if url.find('#search#') == 0:
            article = ""
            category = day = month = year = None
            for param in url.split('#')[2:-1]:
                k, v = param.split('=')
                if k == 'article':
                    article = v
                if k == 'category':
                    category = v
                if k == 'date':
                    day, month, year = v.split('.')
            if day and month and year:
                by_date = (int(day), int(month), int(year))
                publish_date = to_date = by_date
            else:
                by_date = to_date = publish_date = None
            url = self._url(url.split('#')[-1])
            return self.list_content(self._search(url, article, category, by_date, to_date, publish_date), params)
        if url.find("#subcat#") == 0:
            url = url[len("#subcat#"):]
            return self.list_subcategory(self._url(url))
        return self.list_content(util.request(self._url(url)), params)

    def categories(self):
        result = []
        item = self.dir_item()
        item['type'] = 'top'
        item['url'] = "#top#"
        result.append(item)
        item = self.video_item()
        item['title'] = 'Live'
        item['url'] = "live.html"
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Spravodajstvo'
        item['url'] = "#subcat#" + SPRAVODAJSTVO_URL
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Publicistika'
        item['url'] = "#subcat#" + PUBLICISTIKA_URL
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Tlačové Besedy'
        item['url'] = "#subcat#" + TLACOVE_BESEDY_URL
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Online Rozhovory'
        item['url'] = "#subcat#" + ONLINE_ROZHOVORY_URL
        result.append(item)
        return result

    def _list_categories(self, url, start, end, regex):
        result = []
        page = util.request(url)
        data = util.substr(page, start, end)
        for m in re.finditer(regex, data, re.DOTALL):
            item = self.dir_item()
            item['url'] = '#search#category=%s#%s' % (m.group('id'), url)
            item['title'] = m.group('title')
            self._filter(result, item)
        return result

    def list_spravodajstvo_categories(self):
        return self._list_categories(SPRAVODAJSTVO_URL, SPRAVODAJSTVO_START, SPRAVODAJSTVO_END, SPRAVODAJSTVO_ITER_RE)

    def list_publicistika_categories(self):
        return self._list_categories(PUBLICISTIKA_URL, PUBLICISTIKA_START, PUBLICISTIKA_END, PUBLICISTIKA_ITER_RE)

    def list_subcategory(self, url):
        result = []
        item = self.dir_item()
        item['type'] = 'new'
        item['url'] = url
        self._filter(result, item)
        item = self.dir_item()
        item['title'] = '[B]Podľa dátumu[/B]'
        d = date.today()
        item['url'] = "#date#%d#%d#%s" % (d.year, d.month, url)
        self._filter(result, item)
        if SPRAVODAJSTVO_URL in url:
            result.extend(self.list_spravodajstvo_categories())
        elif PUBLICISTIKA_URL in url:
            result.extend(self.list_publicistika_categories())
        return result

    def list_top(self, page):
        result = []
        for item in self.list_top_6hours(page):
            item['title'] = '[6h] ' + item['title']
            result.append(item)
        for item in self.list_top_day(page):
            item['title'] = '[1d] ' + item['title']
            result.append(item)
        for item in self.list_top_week(page):
            item['title'] = '[1t] ' + item['title']
            result.append(item)
        return result

    def _list_top(self, page, start, end, regex):
        result = []
        data = util.substr(page, start, end)
        for m in re.finditer(regex, data, re.DOTALL | re.VERBOSE):
            item = self.video_item()
            item['title'] = "%s (%s)" % (m.group('title'), m.group('views'))
            item['url'] = m.group('url')
            self._filter(result, item)
        return result

    def list_top_6hours(self, page):
        return self._list_top(page, TOP_START_6HOURS, TOP_END_6HOURS, TOP_ITER_RE)

    def list_top_day(self, page):
        return self._list_top(page, TOP_START_DAY, TOP_END_DAY, TOP_ITER_RE)

    def list_top_week(self, page):
        return self._list_top(page, TOP_START_WEEK, TOP_END_WEEK, TOP_ITER_RE)

    def list_content(self, page, params):
        result = []
        data = util.substr(page, LISTING_START, LISTING_END)
        for m in re.finditer(LISTING_ITER_RE, data, re.DOTALL | re.VERBOSE):
            item = self.video_item()
            item['title'] = "%s (%s)" % (m.group('title').strip(), m.group('date').strip())
            item['url'] = m.group('url')
            self._filter(result, item)
        pager_data = util.substr(page, PAGER_START, PAGER_END)
        for m in re.finditer(PAGER_ITER_RE, pager_data, re.DOTALL | re.VERBOSE):
            if not 'type' in m.groupdict():
                continue
            if m.group('type') == 'back':
                item = self.dir_item()
                item['type'] = 'prev'
                item['url'] = params + m.group('url')
                self._filter(result, item)
            elif m.group('type') == 'next':
                item = self.dir_item()
                item['type'] = 'next'
                item['url'] = params + m.group('url')
                self._filter(result, item)
        return result

    def _search(self, url, search_article="", category=None, publish_date=None, by_date=None, to_date=None, where=None):
        #self.info("_search url: '%s', article: '%s', category: '%s', pdate: '%s' bdate: '%s', tdate: '%s', where: '%s'"%(url, search_article, str(category), str(publish_date), str(by_date), str(to_date), str(where)))
        if category is None:
            category = '0'
        if TLACOVE_BESEDY_URL in url:
            category = '147'
        if by_date is None:
            by_date = ""
        else:
            by_date = "%02d.%02d.%d" % (by_date)
        if to_date is None:
            to_date = ""
        else:
            to_date = "%02d.%02d.%d" % (to_date)
        if publish_date is None:
            publish_date = ""
        else:
            publish_date = "%02d.%02d.%d" % (publish_date)
        form = MultiPartForm()
        form.add_field('category', category)
        if PUBLICISTIKA_URL in url:
            form.add_field('publish_date', publish_date)
        else:
            form.add_field('by_date', by_date)
            form.add_field('to_date', to_date)
            if where is None:
                 form.add_field('where[]', 'title')
                 form.add_field('where[]', 'perex')
                 form.add_field('where[]', 'content')
                 form.add_field('where[]', 'tags')
            else:
                for w in where:
                    form.add_field(w[0], w[1])
        form.add_field('search_article', search_article)
        if SPRAVODAJSTVO_URL in url:
            form.add_field('formId', 'articleArchivFilterSpravodajstvo')
        elif PUBLICISTIKA_URL in url:
            form.add_field('formId', 'articleArchivFilterPublicistika')
        elif TLACOVE_BESEDY_URL in url:
            form.add_field('formId', 'articleArchivFilterBesedy')
        request = urllib2.Request(url)
        request.add_header('User-agent', util.UA)
        body = str(form)
        request.add_header('Referer', url)
        request.add_header('Content-type', form.get_content_type())
        request.add_header('Content-length', len(body))
        request.add_data(body)
        try:
            urllib2.urlopen(request).read()
        except RedirectionException:
            return urllib2.urlopen(url).read()

    def date(self, year, month, url):
        result = []
        today = date.today()
        prev_month = month > 1 and month - 1 or 12
        prev_year = prev_month == 12 and year - 1 or year
        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = "#date#%d#%d#%s" % (prev_year, prev_month, url)
        result.append(item)
        for d in calendar.LocaleTextCalendar().itermonthdates(year, month):
            if d.month != month:
                continue
            if d > today:
                break
            item = self.dir_item()
            item['title'] = "%d.%d %d" % (d.day, d.month, d.year)
            item['url'] = "#search#date=%d.%d.%d#%s" % (d.day, d.month, d.year, url)
            self._filter(result, item)
        result.reverse()
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
       item = item.copy()
       if 'live.html' in item['url']:
           result = self._resolve_live(item)
       else:
           result = self._resolve_vod(item)
       result = sorted(result, key=lambda x:x['quality'], reverse=True)
       if len(result) > 0 and select_cb:
           return select_cb(result)
       return result


    def _resolve_vod(self, item):
        resolved = []
        playerdata = util.request(PLAYER_OFFLINE_URL, {'Referer':self._url(item['url'])})
        flashvars = re.search(VIDEO_FLASHVARS_RE, playerdata, re.DOTALL).group(1)
        prefix = re.search(VIDEO_PREFIX_RE, flashvars).group('prefix')
        postfix = re.search(VIDEO_POSTFIX_RE, flashvars).group('postfix').replace('.f4m', '.m3u8').replace("|", "%7C")
        data = util.substr(util.request(self._url(item['url'])), VIDEOTYPE_START, VIDEOTYPE_END)
        video_type_m = re.search(VIDEOTYPE_RE, data)
        video_id = video_type_m.group('id')
        video_type = video_type_m.group('type')
        for quality in QUALITY_POSTFIX.keys():
            if quality == '576p':
                continue
            item = self.video_item()
            item['quality'] = quality
            item['url'] = prefix + VIDEOTEKA_TYPE[video_type] + video_id + QUALITY_POSTFIX[quality] + postfix
            resolved.append(item)
        return resolved
 
    
    def _resolve_live(self, item):
        resolved = []
        playerdata = util.request(PLAYER_ONLINE_URL, {'Referer':self._url(item['url'])})
        flashvars = re.search(VIDEO_FLASHVARS_RE, playerdata, re.DOTALL).group(1)
        quality_low_id = re.search(VIDEO_LIVE_LOW_RE, playerdata).group('low_id')
        quality_medium_id = re.search(VIDEO_LIVE_MEDIUM_RE, playerdata).group('medium_id')
        quality_high_id = re.search(VIDEO_LIVE_HIGH_RE, playerdata).group('high_id')
        qualities = {'576p':quality_high_id,'404p':quality_medium_id,'288p':quality_low_id}
        prefix = re.search(VIDEO_PREFIX_RE, flashvars).group('prefix')
        postfix = re.search(VIDEO_POSTFIX_RE, flashvars).group('postfix').replace('.f4m', '.m3u8').replace("|", "%7C")
        for quality in qualities.keys():
            item = self.video_item()
            item['quality'] = quality
            item['url'] = prefix + qualities[quality] + postfix
            resolved.append(item)
        return resolved
    


# source from http://pymotw.com/2/urllib2/
class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )

        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class TA3HTTPRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        raise RedirectionException()

class RedirectionException(Exception):
    pass
