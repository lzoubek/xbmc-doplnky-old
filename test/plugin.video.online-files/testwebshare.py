import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
from providertestcase import ProviderTestCase

from webshare import WebshareContentProvider

class WebshareProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = WebshareContentProvider
        self.cp = self.provider_class()
        self.list_urls=[]
        self.resolve_items = [{'url':'ident=1de10F12i7'}]
        self.search_keywords = ['avengers']
        self.categories_list = False

