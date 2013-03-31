import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import eserial,befun


class EserialProviderTestCase(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = eserial.EserialContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#show#http://www.eserial.cz/alcatraz/','#list#http://www.eserial.cz/anatomie-lzi/serie/2']
        self.resolve_items = [{'url':'http://www.eserial.cz/anatomie-lzi/video/3673'}]
        self.categories_list = True

class BefunProviderTestCase(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = befun.BefunContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#cat#serialy','#cat#filmy','#cat#filmy/komedie']
        self.resolve_items = [{'url':'http://www.befun.cz/film/1974/avengers-hd-munk'}]
        self.categories_list = True
        self.search_keywords = ['avengers']
