from providertestcase import ResolverTestCase

import streamintoresolver
class StreaminTo(ResolverTestCase):

    def setUp(self):
        self.resolver = streamintoresolver
        self.urls = ['http://streamin.to/embed-wg4ip7hw7hj5-630x360.html']

    def assertions(self,url,results):
        for result in results:
            self.assertTrue(result['quality'] == '360p','Quality is correctly detected')

import youtuberesolver
class Youtube(ResolverTestCase):
    
    def setUp(self):
        self.resolver = youtuberesolver
        self.urls=['http://www.youtube.com/watch?v=KKbUP7brxmY','//www.youtube.com/embed/jY3VBnG1dX4']

import anyfilesresolver
class AnyFiles(ResolverTestCase):
    
    def setUp(self):
        self.resolver = anyfilesresolver
        self.urls=['http://video.anyfiles.pl/w.jsp?id=85590&#038;width=620&#038;height=390&#038;pos=0&#038;skin=1']
