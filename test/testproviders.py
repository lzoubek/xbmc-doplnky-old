import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
from providertestcase import ProviderTestCase

from eserial import EserialContentProvider
class EserialProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = EserialContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#show#http://www.eserial.cz/alcatraz/','#list#http://www.eserial.cz/anatomie-lzi/serie/2']
        self.resolve_items = [{'url':'http://www.eserial.cz/anatomie-lzi/video/3673'}]
        self.categories_list = True

from befun import BefunContentProvider
class BefunProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = BefunContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#cat#serialy','#show#serial/10/alcatraz','#cat#filmy','#cat#filmy/komedie']
        self.resolve_items = [{'url':'http://www.befun.cz/film/1974/avengers-hd-munk'}]
        self.categories_list = True
        self.search_keywords = ['avengers','valecny kun']

from serialy import SerialyczContentProvider
class SerialyczProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = SerialyczContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://www.serialycz.cz/category/home/serialy/beauty-and-the-beast/','category/home/serialy/game-of-thrones/']
        self.resolve_items = [{'url':'http://www.serialycz.cz/2012/03/got-02x00/'}]
        self.categories_list = True

from playserial import PlayserialContentProvider
class PlayserialProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = PlayserialContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#cat#index.php?epizody&serial=californication&nazev=Californication','#show#index.php?serial=californication&serie=2&nazev=Californication']
        self.resolve_items = [{'url':'index.php?id=4614&serial=alcatraz'}]
        self.categories_list = True

from nastojaka import NastojakaContentProvider
class NastojakaProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = NastojakaContentProvider
        self.cp = self.provider_class()
        self.list_urls=['scenky/?page=15&sort=performer']
        self.resolve_items = [{'url':'scenky/287-stara-a-tchyne/'}]
        self.search_keywords = ['matonoha']
        self.categories_list = False

from koukni import KoukniContentProvider
class KoukniProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = KoukniContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://koukni.cz/serialz']
        self.resolve_items = [{'url':'http://koukni.cz/82917405'}]
        self.search_keywords = ['big bang theory']
        self.categories_list = True
