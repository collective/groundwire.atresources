from zope import schema
from zope.interface import Interface

from groundwire.atresources import atresourcesMessageFactory as _


class IATResource(Interface):
    """
    A resource file.
    """

class IATResouceView(Interface):
    """
    A view to display a resource.
    """
    
class IResourceMimeTypeProvider(Interface):
    """
    An adpter to get the mimetype of the resource based on a URL.
    """
    
    def mimetype():
        """
        Returns the mimetype of the resource. This does not have to be a
        real mimetype, and, in fact, probably should not be.
        """
    