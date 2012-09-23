import sys,os,urllib2
import unittest
import providertestcase
import koukni


class BezvadataTest(providertestcase.ProviderTestCase):

	def setUp(self):
		self.provider_class = koukni.KoukniContentProvider
		self.cp = self.provider_class(self.username,self.password)
		self.list_urls=['hledej?strana=10&hledej=dexter']
		self.search_keywords=['once upon a time']
		self.resolve_items = [{'url':'http://koukni.cz/97660082'},{'url':'97660082'}]


if __name__ == '__main__':
    unittest.main()
