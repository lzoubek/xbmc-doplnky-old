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
import simplejson as json
import xbmc,os,random,sys,traceback

import google
class TrackerSettings(object):

	def __init__(self,addon):
		self.services = [google]
		local = xbmc.translatePath(addon.getAddonInfo('profile'))
		if not os.path.exists(local):
			os.makedirs(local)
		self.settingFile = os.path.join(local,'tracking.json')
		
		if os.path.exists(self.settingFile):
			f = open(self.settingFile,'r')
			self.data = json.loads(unicode(f.read().decode('utf-8','ignore')))
			f.close()
		else:
			self.data = {}
			self.data['id'] = {}
			for serv in self.services:
				self.data['id'][serv.__name__] = serv.createInstanceID()
		#	self.data['addons'] = {'script.usage.tracker':{'enabled':True,'terms':-1},'plugin.video.kinotip2.cz':{'enabled':True,'terms':-1}}
			self.data['addons'] = {}
			self.save()
			
	def save(self):
		f = open(self.settingFile,'w')
		f.write(json.dumps(self.data,ensure_ascii=True))
		f.close()

	def getInstanceID(self,service):
		return self.data['id'][service]

	def canDoReport(self,addon):
		subscribers = self.getSubscribers()
		if addon in subscribers:
			return subscribers[addon]['enabled']
	def setCanReport(self,addon,canReport):
		subscribers = self.getSubscribers()
		if addon in subscribers:
			subscribers[addon]['enabled'] = canReport

	def getTermsStringID(self,addon):
		subscribers = self.getSubscribers()
		if addon in subscribers:
			return subscribers[addon]['terms']
	
	def getSubscribers(self):
		return self.data['addons']

	def addAddon(self,addon,subscribed,conditions):
		self.data['addons'][addon] = {}
		self.data['addons'][addon]['enabled'] = subscribed
		self.data['addons'][addon]['terms'] = conditions
		self.save()

class TrackerInfo(object):
	def __init__(self):
		pass

	def _getUserAgent(self,version,language):
		platform = sys.platform
		sp = version.find(' ')
		if sp > 0:
			version = version[:sp]
		if platform.startswith('linux'):
			return 'XBMC/%s (X11; U; Linux i686; %s)' % (version,language)
		if platform.startswith('Win'):
			return 'XBMC/%s (Windows; U; Windows NT; %s)' % (version,language)
		if platform.startswith('darwin'):
			return 'XBMC/%s (Macintosh; U; Intel Mac OS X; %s)' % (version,language)
		else:
			print '[script.usage.tracker] Unknown platform %s, please report a bug, plugin needs to be fixed' % sys.platform
			return 'XBMC/%s (X11; U; Linux i686; %s)' % (version,language)


	def getSystemInfo(self):
		# some stupid defaults
		info = {'colordepth':'24-bit','resolution':'640x480','language':'en','useragent':self._getUserAgent('Unknown','en')}
		
		# get info via JSON RPC, try to be compatible with both dharma & eden APIs
		try:
			data = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "System.GetInfoLabels", "id":1,"params": ["System.BuildVersion","System.ScreenHeight","System.ScreenWidth","System.KenrelVersion","System.Language"]}')
			data = json.loads(data)
		except:
			pass
		try:
			if not 'result' in data:
				data = xbmc.executeJSONRPC('{"jsonrpc" : "2.0", "method": "XBMC.GetInfoLabels", "id" :1, "params": {"labels" : ["System.BuildVersion","System.ScreenHeight","System.ScreenWidth","System.KenrelVersion","System.Language"]}}')
				data = json.loads(data)
		except:
			pass
		# process results
		try:
			info['resolution'] = '%sx%s' %(data['result']['System.ScreenWidth'],data['result']['System.ScreenHeight'])
			info['language'] = getLanguageCode(data['result']['System.Language'])
			info['useragent'] = self._getUserAgent(data['result']['System.BuildVersion'],info['language'])
		except:
			traceback.print_exc()
		return info


def getLanguageCode( id ):
  languages = { 
  	"None"                       : "none",
    "Albanian"                   : "sq",
    "Arabic"                     : "ar",
    "Belarusian"                 : "hy",
    "Bosnian"                    : "bs",
    "BosnianLatin"               : "bs",
    "Bulgarian"                  : "bg",
    "Catalan"                    : "ca",
    "Chinese"                    : "zh",
    "Croatian"                   : "hr",
    "Czech"                      : "cs",
    "Danish"                     : "da",
    "Dutch"                      : "nl",
    "English"                    : "en",
    "Esperanto"                  : "eo",
    "Estonian"                   : "et",
    "Farsi"                      : "fa",
    "Persian"                    : "fa",
    "Finnish"                    : "fi",
    "French"                     : "fr",
    "Galician"                   : "gl",
    "Georgian"                   : "ka",
    "German"                     : "de",
    "Greek"                      : "el",
    "Hebrew"                     : "he",
    "Hindi"                      : "hi",
    "Hungarian"                  : "hu",
    "Icelandic"                  : "is",
    "Indonesian"                 : "id",
    "Italian"                    : "it",
    "Japanese"                   : "ja",
    "Kazakh"                     : "kk",
    "Korean"                     : "ko",
    "Latvian"                    : "lv",
    "Lithuanian"                 : "lt",
    "Luxembourgish"              : "lb",
    "Macedonian"                 : "mk",
    "Malay"                      : "ms",
    "Norwegian"                  : "no",
    "Occitan"                    : "oc",
    "Polish"                     : "pl",
    "Portuguese"                 : "pt",
    "PortugueseBrazil"           : "pb",
    "Portuguese (Brazil)"        : "pb",
    "Brazilian"                  : "pb",
    "Romanian"                   : "ro",
    "Russian"                    : "ru",
    "SerbianLatin"               : "sr",
    "Serbian"                    : "sr",
    "Slovak"                     : "sk",
    "Slovenian"                  : "sl",
    "Spanish"                    : "es",
    "Swedish"                    : "sv",
    "Syriac"                     : "syr",
    "Thai"                       : "th",
    "Turkish"                    : "tr",
    "Ukrainian"                  : "uk",
    "Urdu"                       : "ur",
    "Vietnamese"                 : "vi",
    "English (US)"               : "en",
    "English (UK)"               : "en",
    "Portuguese (Brazilian)"     : "pt-br",
    "Español (Latinoamérica)"    : "es",
    "Español (España)"           : "es",
    "Spanish (Latin America)"    : "es",
    "Español"                    : "es",
    "Spanish (Spain)"            : "es",
    "Chinese (Traditional)"      : "zh",
    "Chinese (Simplified)"       : "zh",
    "Portuguese-BR"              : "pb",
    "All"                        : "all"
  }
  if id in languages:
	return languages[ id ]
  return 'none'
