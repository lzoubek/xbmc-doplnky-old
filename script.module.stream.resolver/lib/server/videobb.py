# -*- coding: UTF-8 -*-
#/*
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

import random,util,re,time

def supports(data):
	return not _regex(data) == None

def url(data):
	if supports(data):
		id = re.sub('http://(www\.)?videobb.com/e/','',data)
		return ['http://s%d.videobb.com/s?v=%s&r=1&t=%d&u=&c=12&start=0' % (random.randint(1,10),id,int(time.time()))]

def _regex(data):
	return re.search('http://(www\.)?videobb.com', data, re.IGNORECASE | re.DOTALL)
