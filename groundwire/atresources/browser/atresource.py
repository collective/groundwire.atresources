from zope.publisher.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.interface import implements
from plone.memoize.instance import memoize
from groundwire.atresources.interfaces.atresource import IATResouceView

class ATResourceView(BrowserView):
    """
    A view to display a resource.
    """
    
    implements(IATResouceView)
        
    @memoize
    def resource_view(self):
        """
        Returns the view for the resource based on its mimetype.
        """
        
        mimetype = self.context.resource_mimetype()
        if mimetype:
            mime_parts = mimetype.split('/')
            for view_name in ['%s_%s' % tuple(mime_parts), mime_parts[0], 'default']:
                view = queryMultiAdapter(
                    (self.context, self.request),
                    name='resource_%s' % view_name,
                )
                if view:
                    return view.__of__(self.context)
        return None
    
    def resource(self):
        """
        Renders the resource.
        """
        
        view = self.resource_view()
        if view:
            return view()
            
        return 'A suitable renderer for this resource could not be found.'
        