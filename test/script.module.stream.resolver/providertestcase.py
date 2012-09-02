import sys,os,urllib2
import ConfigParser
import unittest
sys.path.append( os.path.join ( '..', '..','script.module.stream.resolver','lib') )
sys.path.append( os.path.join ( '..', '..','script.module.stream.resolver','lib','contentprovider') )
import util
import provider

# to be updated by child class
CONFIG_FILE = 'test.config'

class ProviderTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		config = ConfigParser.RawConfigParser()
		try:
			config.read(CONFIG_FILE)
			config.get('Credentials','username')
		except:
			print 'Cannot read config file '+CONFIG_FILE
			config.add_section('Credentials')
			config.set('Credentials', 'username', 'jezz_')
			config.set('Credentials', 'password', 'jezz_')
			with open(CONFIG_FILE, 'wb') as configfile:
    				config.write(configfile)
			print 'Wrote default values to config file'
		cls.username = config.get('Credentials','username')
		cls.password = config.get('Credentials','password')
		

	def test_provider_search(self):
		if 'search' in self.cp.capabilities():
			for keyword in self.search_keywords:
				result = self.cp.search(keyword)
				self.assertTrue(len(result)>0,'Search method must return non-empty array')

	def test_provider_list(self):
		for url in self.list_urls:
			result = self.cp.list(url)
			self.assertTrue(len(result)>0,'Search method must return non-empty array')
			next = None
			prev = None
			for item in result:
				if 'next' == item['type']:
					next = item
				if 'prev' == item['type']:
					prev = item
			self.assertIsNotNone(prev,'Previous navigation item must be returned')
			self.assertIsNotNone(next,'Next navigation item must be returned')
			self.assertNotEqual(prev['url'],next['url'],'Prev and Next URL must NOT be same')

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
		for item in self.resolve_items:
			resolved = self.cp.resolve(item,None)
			self.assertIsNotNone(resolved,'a resolved item was returned')
			self.assertTrue(len(resolved['url']) > 0, ' a non-empty result URL was returned')
			#print(' * Downloading sample file '+resolved['url'])
			#req = urllib2.Request(resolved['url'])
			#response = urllib2.urlopen(req)
			#data = response.read()
			#response.close()
			#print(' * DONE')
			#self.assertTrue(len(data)>10000,'Sample file was retrieved')

	def test_provider_login(self):
		if 'login' in self.cp.capabilities():
			self.assertTrue(self.cp.login(),'login() must return true when valid credentials were provided')
	
	def test_provider_invalid_login(self):
		self.assertFalse(self.provider_class('foo','bar').login(),'login() must return false when invalid credentials were provided')
	
	def test_provider_login_no_credentials(self):
		self.assertFalse(self.provider_class().login(),'login() must return false when no credentials were provided')


