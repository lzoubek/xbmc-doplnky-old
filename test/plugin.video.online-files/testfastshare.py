import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
from providertestcase import ProviderTestCase


from fastshare import FastshareContentProvider
class FastshareProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = FastshareContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://www.fastshare.cz/?term=avengers&type=all']
        self.resolve_items = [{'url':'http://www.fastshare.cz/2050612/avengers-avengers-the-2012-dvdrip-xvid-cz.avi'}]
        self.search_keywords = ['avengers']
        self.categories_list = False

    @unittest.skipIf(os.getenv('MODE')=='auto', "Requires user interaction, skipped when environment var MODE=auto exists")	
    def test_resolve_interactive(self):
        self.cp = self.provider_class()
        def callback(params):
            print('captcha ID: %s IMG: %s' % (params['id'],params['img']))
            captcha = raw_input('Please check IMG and Enter captcha: ')
            return captcha

        resolved = self.cp.resolve({'url':'http://www.fastshare.cz/1676405/winrar-4.20-32-64-bit-cz-sk.zip'},callback,None)
        self.assertIsNotNone(resolved,'a resolved item was returned')
        self.assertTrue(len(resolved['url']) > 0, ' a non-empty result URL was returned')
        print(' * Downloading sample file '+resolved['url'])
        req = urllib2.Request(resolved['url'])
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        print(' * DONE')
        self.assertTrue(len(data)>10000,'Sample file was retrieved')
    
    def test_resolve(self):
        self.cp = self.provider_class()
        self.count = -1
        def callback(params):
            self.assertIsNotNone(params,'params passed to callback function must have a value')
            self.assertIsNotNone(params['id'],'id param passed to callback function must have a value')
            self.assertIsNotNone(params['img'],' img param passed to callback function must have a value')
            self.count+=1
        resolved = self.cp.resolve({'url':'1676405/winrar-4.20-32-64-bit-cz-sk.zip'},callback)
        self.assertIsNone(resolved,'Nothing is resolved when callback method did not provide values')
        self.assertTrue(self.count==0,'callback method was called exactly once')
        def callback(params):
            self.count+=1
            if self.count<5:
                return 'xxxxx'

        resolved = self.cp.resolve({'url':'1676405/winrar-4.20-32-64-bit-cz-sk.zip'},callback)
        self.assertTrue(self.count==5,'callback method was called 4 times because invalid codes were supplied'+str(self.count))

