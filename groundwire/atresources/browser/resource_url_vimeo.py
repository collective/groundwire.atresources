from zope.publisher.browser import BrowserPage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from urlparse import urlparse

class VimeoURL(BrowserPage):
    """
    A view to display a Vimeo video.
    """
    
    __call__ = ViewPageTemplateFile('resource_url_vimeo.pt')
    
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
        Returns the vimeo ID of the movie.
        """
        
        url = self.context.getUrl().strip()
        return urlparse(url)[2].replace('/', '')
