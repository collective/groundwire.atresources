from zope.publisher.browser import BrowserPage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urlparse import urlparse
from cgi import parse_qs
from plone.memoize import instance

class YouTubeURL(BrowserPage):
    """
    A view to display a YouTube video.
    """
    
    __call__ = ViewPageTemplateFile('resource_url_youtube.pt')
    
    @instance.memoize
    def url_scheme(self):
        """
        Returns http or https.
        """
        
        url = self.context.getUrl().strip()
        return urlparse(url)[0]
    
    @instance.memoize
    def movie_id(self):
        """
        Returns the YouTube ID of the movie.
        """
        
        url = self.context.getUrl().strip()
        url_parts = urlparse(url)
        qs = parse_qs(url_parts[4])
        if 'v' in qs.keys():
            return qs['v'][0]
        if url_parts[1] == 'youtu.be':
            return url_parts[2].lstrip('/')
        return ''
        
        