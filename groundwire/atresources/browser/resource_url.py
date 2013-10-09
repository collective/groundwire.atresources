from zope.publisher.browser import BrowserPage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from urlparse import urlparse

WEB_MIMETYPES = [
    'text/html',
    'application/x-httpd-php',
]

GOOGLEDOCS_MIMETYPES = [
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/pdf',
    'application/illustrator',
    'image/x-psd',
    'image/x-photoshop',
]

class URL(BrowserPage):
    """
    A view to display a generic URL.
    """
    
    __call__ = ViewPageTemplateFile('resource_url.pt')
    
    @property
    def web_mimetypes(self):
        """
        Returns a list of mimetypes that should be considered web sites.
        """
        
        return WEB_MIMETYPES
    
    @instance.memoize
    def guess_mimetype(self):
        """
        Tries to determine the mimetype of the file based on the file extension.
        Returns None if no mimetype matches.
        """
        
        url = self.context.getUrl().strip()
        path_parts = urlparse(url)[2].split('/')
        if path_parts:
            filename = path_parts.pop()
            mimetypes = getToolByName(self.context, 'mimetypes_registry')
            return mimetypes.lookupExtension(filename)
        return None
        
    def icon_url(self):
        """
        Returns the URL to the icon for this mimetype.
        """
        
        mimetype = self.guess_mimetype()
        icon = getattr(mimetype, 'icon_path', None)
        if icon:
            portal_url = self.context.restrictedTraverse('@@plone_portal_state').portal_url()
            return '%s/%s' % (portal_url, icon)
        return None
        
    def use_googledocs_viewer(self):
        """
        Determines whether the Google Docs viewer should be displayed.
        """
        
        return self.guess_mimetype() in GOOGLEDOCS_MIMETYPES
