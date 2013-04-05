import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import bezvadata

providertestcase.CONFIG_FILE = 'testbezvadata.config'

class BezvadataTest(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = bezvadata.BezvadataContentProvider
        self.cp = self.provider_class(self.username,self.password)
        self.list_urls=['http://bezvadata.cz/vyhledavani/?s=video&page=2']
        self.search_keywords=['jachyme hod ho do stroje']
        self.categories_list = False
        self.resolve_items = []

    def _test_resolve(self):
        self.cp = self.provider_class()
        self.count = -1
        def callback(params):
            self.assertIsNotNone(params,'params passed to callback function must have a value')
            self.assertIsNotNone(params['id'],'id param passed to callback function must have a value')
            self.assertIsNotNone(params['img'],' img param passed to callback function must have a value')
            self.count+=1
        resolved = self.cp.resolve({'url':'http://bezvadata.cz/stahnout/133002_skyfall-2012-cz-bdrip.akcni-novinky.avi'},callback,None)
        self.assertIsNone(resolved,'Nothing is resolved when callback method did not provide values')
        self.assertTrue(self.count==0,'callback method was called exactly once (was %d)' %self.count)
