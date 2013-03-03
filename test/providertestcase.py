import sys,os,urllib2
import ConfigParser
import unittest

filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename, '..','script.module.stream.resolver','lib') )
sys.path.append( os.path.join ( filename , '..','script.module.stream.resolver','lib','contentprovider') )
import provider
import util

def import_dir(lib):
    if os.path.exists(lib):
        sys.path.append(lib)
        for module in os.listdir(lib):
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            module = module[:-3]
            try:
                exec 'import %s' % module
                util.debug('imported %s' % module)
            except:
#                traceback.print_exc()
                util.error('Failed to import %s' % module)

for addon in os.listdir(os.path.join(os.path.realpath(filename),'..')):
    if addon.find('plugin.video')>=0:
        lib = os.path.join(filename,'..',addon,'resources','lib')
        import_dir(lib)       


# to be updated by child class
CONFIG_FILE = 'test.config'

class ProviderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(CONFIG_FILE)
            config.get('Credentials','username')
        except:
            print 'Cannot read config file '+CONFIG_FILE
            config.add_section('Credentials')
            config.set('Credentials', 'username', 'jezz_')
            config.set('Credentials', 'password', 'jezz_')
            with open(CONFIG_FILE, 'wb') as configfile:
                config.write(configfile)
            print 'Wrote default values to config file'
        cls.username = config.get('Credentials','username')
        cls.password = config.get('Credentials','password')


    def test_provider_search(self):
        if 'search' in self.cp.capabilities():
            for keyword in self.search_keywords:
                result = self.cp.search(keyword)
                self.assertTrue(len(result)>0,'Search method must return non-empty array for keyword \'%s\'' % keyword)

    def test_provider_list(self):
        for url in self.list_urls:
            result = self.cp.list(url)
            self.assertTrue(len(result)>0,'List method must return non-empty array for \'%s\''% url)

    def test_provider_list_filtered(self):
        def filter(item):
            return False
        for url in self.list_urls:
            result = self.provider_class(filter=filter).list(url)
            count = 0
            for item in result:
                if item['type'] == 'video':
                    count+=1
            self.assertTrue(count == 0,'Provider must return 0 video items when when filtering that stops everyting is applied')

    def test_provider_resolve(self):
        def select_cb(items):
            return items[0]
        for item in self.resolve_items:
            resolved = self.cp.resolve(item,None,select_cb)
            self.assertIsNotNone(resolved,'a resolved item was returned')
            self.assertTrue(len(resolved['url']) > 0, ' a non-empty result URL was returned')
            #print(' * Downloading sample file '+resolved['url'])
            #req = urllib2.Request(resolved['url'])
            #response = urllib2.urlopen(req)
            #data = response.read()
            #response.close()
            #print(' * DONE')
            #self.assertTrue(len(data)>10000,'Sample file was retrieved')

    def test_provider_login(self):
        if 'login' in self.cp.capabilities():
            self.assertTrue(self.cp.login(),'login() must return true when valid credentials were provided')
            self.assertTrue(self.cp.login(),'login() must return true even when we are already logged in')

    def test_provider_invalid_login(self):
        self.assertFalse(self.provider_class('foo','bar').login(),'login() must return false when invalid credentials were provided')

    def test_provider_login_no_credentials(self):
        self.assertFalse(self.provider_class().login(),'login() must return false when no credentials were provided')


