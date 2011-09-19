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

# resolver for all servers that apparently do NOT work

import re,util

def url(data):
	for f in [_videotube]:
		if f(data) == True:
			return ''	

def _videotube(data):
	m = re.search('src=\"(?P<js>http\://www.videotube.sk/js[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	return not m == None
		
