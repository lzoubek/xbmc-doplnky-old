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

import googletracker
class TrackerSettings(object):

    def __init__(self,addon):
        self.services = [googletracker]
        local = xbmc.translatePath(addon.getAddonInfo('profile'))
        if not os.path.exists(local):
            os.makedirs(local)
        self.settingFile = os.path.join(local,'tracking.json')

        if os.path.exists(self.settingFile):
            f = open(self.settingFile,'r')
            self.data = json.loads(unicode(f.read().decode('utf-8','ignore')))
            f.close()
            for serv in self.services:
                if not serv.__name__ in self.data['id'].keys():
                    self.data['id'][serv.__name__] = serv.createInstanceID()
                    self.save()
        else:
            self.data = {}
            self.data['id'] = {}
            for serv in self.services:
                self.data['id'][serv.__name__] = serv.createInstanceID()
            self.data['addons'] = {}
            self.save()

    def save(self):
        f = open(self.settingFile,'w')
        f.write(json.dumps(self.data,ensure_ascii=True))
        f.close()

    def getInstanceID(self,service):
        return self.data['id'][service]

    def isReportingEnabled(self):
        if 'report-enabled' in self.data:
            return self.data['report-enabled']

    def setReportingEnabled(self,value):
        self.data['report-enabled'] = value

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
        if platform.startswith('win'):
            return 'XBMC/%s (Windows; U; Windows NT; %s)' % (version,language)
        if platform.startswith('darwin'):
            return 'XBMC/%s (Mac; U; Intel Mac OS X; %s)' % (version,language)
        else:
            print '[script.usage.tracker] Unknown platform %s, please report a bug, plugin needs to be fixed' % sys.platform
            return 'XBMC/%s (X11; U; Unknown i686; %s)' % (version,language)


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
            "none"                       : "none",
            "albanian"                   : "sq",
            "arabic"                     : "ar",
            "belarusian"                 : "hy",
            "bosnian"                    : "bs",
            "bosnianLatin"               : "bs",
            "bulgarian"                  : "bg",
            "catalan"                    : "ca",
            "chinese"                    : "zh",
            "croatian"                   : "hr",
            "czech"                      : "cs",
            "danish"                     : "da",
            "dutch"                      : "nl",
            "english"                    : "en",
            "esperanto"                  : "eo",
            "Estonian"                   : "et",
            "farsi"                      : "fa",
            "persian"                    : "fa",
            "finnish"                    : "fi",
            "french"                     : "fr",
            "galician"                   : "gl",
            "georgian"                   : "ka",
            "german"                     : "de",
            "greek"                      : "el",
            "hebrew"                     : "he",
            "hindi"                      : "hi",
            "hungarian"                  : "hu",
            "icelandic"                  : "is",
            "indonesian"                 : "id",
            "italian"                    : "it",
            "japanese"                   : "ja",
            "kazakh"                     : "kk",
            "korean"                     : "ko",
            "latvian"                    : "lv",
            "lithuanian"                 : "lt",
            "luxembourgish"              : "lb",
            "macedonian"                 : "mk",
            "malay"                      : "ms",
            "norwegian"                  : "no",
            "occitan"                    : "oc",
            "polish"                     : "pl",
            "portuguese"                 : "pt",
            "portuguesebrazil"           : "pb",
            "portuguese (brazil)"        : "pb",
            "brazilian"                  : "pb",
            "romanian"                   : "ro",
            "russian"                    : "ru",
            "serbianLatin"               : "sr",
            "serbian"                    : "sr",
            "serbian (syrillic)"         : "sr",
    "slovak"                     : "sk",
    "slovenian"                  : "sl",
    "spanish"                    : "es",
    "swedish"                    : "sv",
    "syriac"                     : "syr",
    "thai"                       : "th",
    "turkish"                    : "tr",
    "ukrainian"                  : "uk",
    "urdu"                       : "ur",
    "vietnamese"                 : "vi",
    "english (us)"               : "en",
    "english (uk)"               : "en",
    "portuguese (brazilian)"     : "pt-br",
    "español (latinoamérica)"    : "es",
    "español (españa)"           : "es",
    "spanish (latin America)"    : "es",
    "español"                    : "es",
    "spanish"                    : "es",
    "spanish (mexico)"           : "es",
    "spanish (spain)"            : "es",
    "chinese (traditional)"      : "zh",
    "chinese (simplified)"       : "zh",
    "portuguese-br"              : "pb",
    "all"                        : "all"
  }
    id = id.lower()
    if id in languages:
        return languages[ id ]
    print '[script.usage.tracker] Cannot detect language code from language: %s, please report a bug, plugin needs to be fixed' % id
    return id
