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
        self.resolve_items = [{'url':'http://eserial.cz/mentalista/video/1819'}]
        self.categories_list = True

from befun import BefunContentProvider
class BefunProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = BefunContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#cat#serialy','#show#serial/10/alcatraz','#cat#filmy','#cat#filmy/komedie']
        self.resolve_items = [{'url':'http://www.befun.cz/film/4613/proc-jsem-se-jen-zenil-sd-munk'}]
        self.categories_list = True
        self.search_keywords = ['avengers','valecny kun']

from tvsosac import TVSosacContentProvider
class TVSosacProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = TVSosacContentProvider
        self.cp = self.provider_class()
        self.list_urls=['cs/tv-shows-a-z/m','#serie#cs/detail/misfits-zmetci']
        self.resolve_items = [{'url':'http://tv.sosac.ph/cs/player/once-upon-a-time-s2-e22'}]
        self.categories_list = True
        self.search_keywords = ['avengers','valecny kun']

from mtrsk import MtrSkContentProvider
class MtrSkProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = MtrSkContentProvider
        self.cp = self.provider_class()
        self.list_urls=[]
        self.resolve_items = [{'url':'http://kdah.mtr.sk/videoarchiv/2013/2013-11-04_FILMTIP.mp4'}]
        self.categories_list = False
        self.search_keywords = []

from serialy import SerialyczContentProvider
class SerialyczProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = SerialyczContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://www.serialycz.cz/category/home/serialy/beauty-and-the-beast/','category/home/serialy/game-of-thrones/']
        self.resolve_items = [{'url':'http://www.blau.mablog.eu/?p=65'}]
        self.categories_list = True

from playserial import PlayserialContentProvider
class PlayserialProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = PlayserialContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#cat#index.php?epizody&serial=californication&nazev=Californication','#show#index.php?serial=californication&serie=2&nazev=Californication']
        self.resolve_items = [{'url':'index.php?id=11608&serial=simpsonovi'}]
        self.categories_list = True


#from nastojaka import NastojakaContentProvider
#class NastojakaProviderTestCase(ProviderTestCase):
#
#    def setUp(self):
#        self.provider_class = NastojakaContentProvider
#        self.cp = self.provider_class()
#        self.list_urls=['scenky/?page=15&sort=performer']
#        self.resolve_items = [{'url':'scenky/287-stara-a-tchyne/'}]
#        self.search_keywords = ['matonoha']
#        self.categories_list = False

from pohadkar import PohadkarContentProvider
class PohadkarProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = PohadkarContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#list#4','pohadka/s-certy-nejsou-zerty/video/']
        self.resolve_items = [{'url':'video/s-certy-nejsou-zerty-pivo/'}]
        self.search_keywords = ['vcelka maja']
        self.categories_list = True

from koukni import KoukniContentProvider
class KoukniProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = KoukniContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://koukni.cz/serialz']
        self.resolve_items = [{'url':'http://koukni.cz/39862282'}]
        self.search_keywords = ['big bang theory']
        self.categories_list = True
        
from videacesky import VideaceskyContentProvider
class VideaceskyProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = VideaceskyContentProvider
        self.cp = self.provider_class()
        self.list_urls=['http://www.videacesky.cz/category/navody-dokumenty-pokusy']
        self.resolve_items = [{'url':'talk-show-rozhovory/nathan-fillion-potreti-u-jimmyho-kimmela'},
                              {'url':'navody-dokumenty-pokusy/pravdiva-fakta-o-vrubounovi'}]
        self.search_keywords = ['fotbal']
        self.categories_list = True
        
from rtvs import RtvsContentProvider
class RtvsProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = RtvsContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#listaz#?letter=a',
                        'http://www.rtvs.sk/televizia/program/detail/4348/nikto-nie-je-dokonaly/archiv?date=04.06.2013',
                        'http://www.rtvs.sk/tv.programmes.detail/archive/4348?calendar-date=2013-5&date=04.06.2013&do=calendar-changeMonth',
                        'http://www.rtvs.sk/televizia/program/detail/2577/a3um/archiv?date=25.11.2012']
        self.resolve_items = [{'url':'http://www.rtvs.sk/televizia/program/detail/4348/nikto-nie-je-dokonaly/archiv?date=04.06.2013'},
                              {'url':'http://ww.rtvs.sk/tv.programmes.detail/archive/4348?calendar-date=04.06.2013&date=04.06.2013&do=calendar-changeDate'}]
        self.categories_list = True
        

from joj import JojContentProvider
class JojProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = JojContentProvider
        self.cp = self.provider_class()
        self.list_urls=['#top#',
                        "#cat#http://www.joj.sk/archiv.html",
                        "#cat##rel#http://www.joj.sk/archiv.html/?type=relacie",
                        '#subcat##showon#http://www.joj.sk/archiv.html/?type=relacie',
                        '#subcat##showoff#http://www.joj.sk/archiv.html/?type=relacie',
                        '#series#http://buckovci.joj.sk/buckovci-archiv/2013-05-06-buckovci-2-slnko-seno-dedina-finale-serie.html',
                        '#episodes##0#http://buckovci.joj.sk/ajax.json?contentId=16363&serie=4679&page=36160&actualAlias=2013-05-06-buckovci-2-slnko-seno-dedina-finale-serie',]
        self.resolve_items = [{'url':'http://panelak.joj.sk/panelak-epizody/2013-08-19-panelak.html'}]
        self.categories_list = True
        
        
from barrandov import BarrandovContentProvider
class BarrandovProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = BarrandovContentProvider
        self.cp = self.provider_class()
        self.list_urls=['video/hlavni-zpravy/']
        self.resolve_items = [{'url':'http://www.barrandov.tv/video/17085-hlavni-zpravy-17-9-2013'}]
        self.categories_list = True
        
from gordonura import GordonUraContentProvider
class GordonUraContentProviderTestCase(ProviderTestCase):

    def setUp(self):
        self.provider_class = GordonUraContentProvider
        self.cp = self.provider_class()
        self.list_urls=['?tag=KN-online']
        self.resolve_items = [{'url':'http://gordon.ura.cz/?p=3219'}]
        self.categories_list = True
