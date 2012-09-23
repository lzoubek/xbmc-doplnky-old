import sys,os,urllib2
import unittest
sys.path.append( os.path.join ( '..', '..','script.module.stream.resolver','lib') )
sys.path.append( os.path.join ( '..', '..','script.module.stream.resolver','lib','contentprovider') )
sys.path.append( os.path.join ( '..', '..','plugin.video.playserial.cz','resources','lib') )
import playserial

# to be updated by child class

class PlayserialProviderTestCase(unittest.TestCase):

	def setUp(self):
		self.provider_class = playserial.PlayserialContentProvider
		self.cp = self.provider_class()
		self.list_urls=['#cat#index.php?epizody&serial=californication&nazev=Californication','#show#index.php?serial=californication&serie=2&nazev=Californication']
		self.resolve_items = [{'url':'index.php?id=4614&serial=alcatraz'}]

	def test_provider_list(self):
		for url in self.list_urls:
			result = self.cp.list(url)
			self.assertTrue(len(result)>0,'Search method must return non-empty array')

	def test_provider_list_filtered(self):
		def filter(item):
			return False
		for url in self.list_urls:
			result = self.provider_class(filter=filter).list(url)
			count = 0
			for item in result:
				if item['type'] == 'video':
					count+=1
			self.assertTrue(count == 0,'Provider must return 0 video items when when filtering that stops everyting is applied')

	def test_provider_resolve(self):
		# define dummy selector
		def select_cb(items):
			return items[0]
		for item in self.resolve_items:
			resolved = self.cp.resolve(item,None,select_cb)
			self.assertIsNotNone(resolved,'a resolved item was returned')
			self.assertTrue(len(resolved['url']) > 0, ' a non-empty result URL was returned')

	def test_categories(self):
		if 'categories' in self.cp.capabilities():
			assertTrue(len(self.cp.categories()) > 0,'At least 1 category must be returned')
