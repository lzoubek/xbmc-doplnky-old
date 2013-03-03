import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import nastojaka


class NastojakaProviderTestCase(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = nastojaka.NastojakaContentProvider
        self.cp = self.provider_class()
        self.list_urls=['scenky/?page=15&sort=performer']
        self.resolve_items = [{'url':'scenky/287-stara-a-tchyne/'}]
        self.search_keywords = ['matonoha']
        self.categories_list = False

