import sys,os,urllib2
import unittest
import providertestcase
import hellspy

providertestcase.CONFIG_FILE = 'testhellspy.config'

class HellspyTest(providertestcase.ProviderTestCase):

	def setUp(self):
		self.provider_class = hellspy.HellspyContentProvider
		self.cp = self.provider_class(self.username,self.password)
		self.list_urls=['http://www.hellspy.cz/search/?p=2&q=avengers']
		self.search_keywords=['lidice']
		self.resolve_items = [{'url':'http://www.hellspy.cz/hacking-mobilu-staci-zadat-tel-a-vidite-veskera-volana-cisla-a-psane-sms-zip/6694059?_ds=6'}]


if __name__ == '__main__':
    unittest.main()
