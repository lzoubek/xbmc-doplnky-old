from providertestcase import ResolverTestCase

import streamintoresolver
class StreaminTo(ResolverTestCase):

    def setUp(self):
        self.resolver = streamintoresolver
        self.urls = ['http://streamin.to/embed-wg4ip7hw7hj5-630x360.html']

    def assertions(self,url,results):
        for result in results:
            self.assertTrue(result['quality'] == '360p','Quality is correctly detected')
