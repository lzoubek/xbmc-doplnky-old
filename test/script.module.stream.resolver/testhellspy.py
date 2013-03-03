import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import hellspy

providertestcase.CONFIG_FILE = 'testhellspy.config'

class HellspyTest(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = hellspy.HellspyContentProvider
        self.cp = self.provider_class(self.username,self.password)
        self.list_urls=['http://www.hellspy.cz/search/?p=2&q=avengers']
        self.search_keywords=['lidice']
        self.resolve_items = [{'url':'http://www.hellspy.cz/ve-stinu-2012-dvdrip-xvid-ac3-cz-avi/10608051?_ds=4'}]


if __name__ == '__main__':
    unittest.main()
