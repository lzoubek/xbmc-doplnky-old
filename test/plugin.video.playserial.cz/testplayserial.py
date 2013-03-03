import sys,os,urllib2
import unittest
filename = os.path.dirname( os.path.realpath(__file__) )
sys.path.append( os.path.join ( filename,'..' ) )
import providertestcase
import playserial


class PlayserialProviderTestCase(providertestcase.ProviderTestCase):

	def setUp(self):
		self.provider_class = playserial.PlayserialContentProvider
		self.cp = self.provider_class()
		self.list_urls=['#cat#index.php?epizody&serial=californication&nazev=Californication','#show#index.php?serial=californication&serie=2&nazev=Californication']
		self.resolve_items = [{'url':'index.php?id=4614&serial=alcatraz'}]

