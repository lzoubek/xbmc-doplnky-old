import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import eserial


class EserialProviderTestCase(providertestcase.ProviderTestCase):

    def setUp(self):
        self.provider_class = eserial.EserialContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#show#http://www.eserial.cz/alcatraz/','#list#http://www.eserial.cz/anatomie-lzi/serie/2']
        self.resolve_items = [{'url':'http://www.eserial.cz/anatomie-lzi/video/3673'}]
        self.categories_list = True
