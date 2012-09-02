import sys,os,urllib2
import unittest
import providertestcase
import bezvadata

providertestcase.CONFIG_FILE = 'testbezvadata.config'

class BezvadataTest(providertestcase.ProviderTestCase):

	def setUp(self):
		self.provider_class = bezvadata.BezvadataContentProvider
		self.cp = self.provider_class(self.username,self.password)
		self.list_urls=['http://bezvadata.cz/vyhledavani/?s=video&page=2']
		self.search_keywords=['jachyme hod ho do stroje']
		self.resolve_items = [{'url':'http://bezvadata.cz/stahnout/41884_video-roll.jpg'},{'url':'stahnout/41884_video-roll.jpg'}]


if __name__ == '__main__':
    unittest.main()
