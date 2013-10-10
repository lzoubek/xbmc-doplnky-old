import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import ulozto

providertestcase.CONFIG_FILE = 'testulozto.config'

class UloztoProviderTest(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = ulozto.UloztoContentProvider
        self.cp = self.provider_class(self.username,self.password)
        self.list_urls=['http://www.ulozto.cz/hledej/?media=video&q=avengers']
        self.search_keywords=['lidice']
        self.resolve_items = [{'url':'http://www.ulozto.cz/xiurFab/icq-dll'}]
        self.categories_list = False

    def test_resolve(self):
        self.cp = self.provider_class()
        self.count = -1
        def callback(params):
            self.assertIsNotNone(params,'params passed to callback function must have a value')
            self.assertIsNotNone(params['id'],'id param passed to callback function must have a value')
            self.assertIsNotNone(params['img'],' img param passed to callback function must have a value')
            self.count+=1
        resolved = self.cp.resolve({'url':'http://www.ulozto.cz/xKE15B7K/avengers-akcni-sci-fi-2012-cz-avi'},callback)
        self.assertIsNone(resolved,'Nothing is resolved when callback method did not provide values')
        self.assertTrue(self.count==0,'callback method was called exactly once')
        def callback(params):
            self.count+=1
            if self.count<5:
                return 'xxxxx'

        resolved = self.cp.resolve({'url':'http://www.ulozto.cz/xKE15B7K/avengers-akcni-sci-fi-2012-cz-avi'},callback)
        self.assertTrue(self.count==5,'callback method was called 4 times because invalid codes were supplied')

    @unittest.skipIf(os.getenv('MODE')=='auto', "Requires user interaction, skipped when environment var MODE=auto exists")	
    def test_resolve_interactive(self):
        self.cp = self.provider_class()
        def callback(params):
            print('captcha ID: %s IMG: %s' % (params['id'],params['img']))
            captcha = raw_input('Please check IMG and Enter captcha: ')
            return captcha

        resolved = self.cp.resolve({'url':'http://www.ulozto.cz/xGKae1u/razor1911-rar'},callback)
        self.assertIsNotNone(resolved,'a resolved item was returned')
        self.assertTrue(len(resolved['url']) > 0, ' a non-empty result URL was returned')
        print(' * Downloading sample file '+resolved['url'])
        req = urllib2.Request(resolved['url'])
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        print(' * DONE')
        self.assertTrue(len(data)>10000,'Sample file was retrieved')
