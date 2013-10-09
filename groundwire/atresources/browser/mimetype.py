from zope.component import adapts
from zope.interface import implements
from groundwire.atresources.interfaces.atresource import IATResource, \
    IResourceMimeTypeProvider
from urlparse import urlparse

class BaseMimeTypeProvider(object):
    """
    An adpter to get the mimetype of the resource based on a URL.
    """
    
    adapts(IATResource)
    implements(IResourceMimeTypeProvider)
    
    def __init__(self, context):
        self.context = context

    def mimetype(self):
        """
        Returns the mimetype of the resource. This does not have to be a
        real mimetype, and, in fact, probably should not be.
        """
        return None
        
class VideoMimeTypeProvider(BaseMimeTypeProvider):
    """
    An adpter to get the mimetype of YouTube and Vimeo URLs.
    """

    def mimetype(self):
        """
        Returns the mimetype for YouTube and Vimeo links.
        """
        
        url = self.context.getUrl().strip()
        url_parts = urlparse(url)
        if url_parts[1] == 'www.youtube.com' and url_parts[2] == '/watch':
            return 'url/youtube'
        if url_parts[1] == 'youtu.be':
            return 'url/youtube'
        if url_parts[1] == 'vimeo.com':
            return 'url/vimeo'
            
class AudioMimeTypeProvider(BaseMimeTypeProvider):
    """
    An adpter to get the mimetype of MP3 URLs.
    """

    def mimetype(self):
        """
        Returns the mimetype for MP3 links.
        """

        url = self.context.getUrl().strip()
        if url.endswith('.mp3'):
            return 'url/mp3'