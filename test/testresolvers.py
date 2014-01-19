from providertestcase import ResolverTestCase

import streamintoresolver
class StreaminTo(ResolverTestCase):

    def setUp(self):
        self.resolver = streamintoresolver
        self.urls = ['http://streamin.to/embed-wg4ip7hw7hj5-630x360.html']

    def assertions(self,url,results):
        for result in results:
            self.assertTrue(result['quality'] == '360p','Quality is correctly detected')

import streamujtvresolver

class StreamujTv(ResolverTestCase):

    def setUp(self):
        self.resolver = streamujtvresolver
        self.urls = ['http://www.streamuj.tv/video/48246-0661-1c3fd6-d036c1f618ee20c710d3?affid=174&width=610&height=360&remote=1']

    def assertions(self,url,results):
        for result in results:
            self.assertTrue(len(result['subs']) > 0, 'Subs were detected')

import playedtoresolver
class PlayedTo(ResolverTestCase):

    def setUp(self):
        self.resolver = playedtoresolver
        self.urls = ['http://played.to/embed-s16qcl6cr7fn-630x360.html','http://played.to/embed-s16qcl6cr7fn-630x360.html']

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
        self.urls=['http://video.anyfiles.pl/w.jsp?id=85626&width=620&height=349&pos=&skin=0',
                'http://video.anyfiles.pl/w.jsp?id=85590&#038;width=620&#038;height=390&#038;pos=0&#038;skin=1']
