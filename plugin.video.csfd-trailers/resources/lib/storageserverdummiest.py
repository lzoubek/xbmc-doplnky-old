'''
     StorageServer override.
     Version: 1.0
'''
import xbmc
import os
try:
    import hashlib
except:
    import md5

try:
	import xbmcvfs
	def pathexists(path):
		return xbmcvfs.exists(path)
except:
	def pathexists(path):
		return os.path.exists(path)

import time
import sys
import simplejson as json
if hasattr(sys.modules["__main__"], "settings"):
    settings = sys.modules["__main__"].settings
else:
    settings = False
__addon__ = sys.modules['__main__'].__addon__

class StorageServer:
    def __init__(self, table=False,cacheTime=0):
        self.table = table
        if settings:
            temporary_path = xbmc.translatePath(settings.getAddonInfo("profile"))
            if not pathexists(temporary_path):
                os.makedirs(temporary_path)

        return None

    def cacheFunction(self, funct=False, *args):
        result = ""
        if not settings:
            return funct(*args)
        elif funct and self.table:
            name = repr(funct)
            if name.find(" of ") > -1:
                name = name[name.find("method") + 7:name.find(" of ")]
            elif name.find(" at ") > -1:
                name = name[name.find("function") + 9:name.find(" at ")]

            # Build unique name
            if "hashlib" in globals():
                keyhash = hashlib.md5()
            else:
                keyhash = md5.new()

            for params in args:
                if isinstance(params, dict):
                    for key in sorted(params.iterkeys()):
                        if key not in ["new_results_function"]:
                            keyhash.update("'%s'='%s'" % (key, params[key]))
                elif isinstance(params, list):
                    keyhash.update(",".join(["%s" % el for el in params]))
                else:
                    try:
                        keyhash.update(params)
                    except:
                        keyhash.update(str(params))

            name += "-" + keyhash.hexdigest() + ".cache"

            path = os.path.join(xbmc.translatePath(settings.getAddonInfo("profile")).decode("utf-8"), name)
            if pathexists(path) and os.path.getmtime(path) > time.time() - 3600:
                print "Getting cache : " + repr(path)
                temp = open(path)
                result = eval(temp.read())
                temp.close()
            else:
                print "Setting cache: " + repr(path)
                result = funct(*args)
                if len(result) > 0:
                    temp = open(path, "w")
                    temp.write(repr(result))
                    temp.close()

        return result

    def set(self, name, data):
	mydata = {}
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,'cache.json')
	if os.path.exists(local):
		f = open(local,'r')
		content = f.read()
		mydata = json.loads(unicode(content.decode('utf-8','ignore')))
		f.close()
	mydata[name] = data
	f = open(local,'w')
	f.write(json.dumps(mydata,ensure_ascii=True))
	f.close()
	return ''

    def get(self, name):
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	local = os.path.join(local,'cache.json')
	if not os.path.exists(local):
		return ''
	f = open(local,'r')
	data = f.read()
	mydata  = json.loads(unicode(data.decode('utf-8','ignore')))
	f.close()
	if name in mydata:
		return mydata[name]
        return ''

    def setMulti(self, name, data):
        return ""

    def getMulti(self, name, items):
        return ""

    def lock(self, name):
        return False

    def unlock(self, name):
        return False

    def delete(self,name):
        try:
		local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
		local = os.path.join(local,'cache.json')
		os.remove(local)
	except:
		pass
	return False
