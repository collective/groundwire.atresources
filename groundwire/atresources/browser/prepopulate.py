from urllib import urlencode
from zExceptions import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from groundwire.atresources.config import ADD_PERMISSIONS

class PrepopulateResource(BrowserView):
    """
    Prepopulates a new resource with title and URL.
    """
    
    def __call__(self):
        self.request.response.setHeader('Expires', 'Sat, 01 Jan 2000 00:00:00 GMT')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        
        membership = getToolByName(self.context, 'portal_membership')
        if not membership.checkPermission(ADD_PERMISSIONS['ATResource'], self.context):
            raise Unauthorized
        
        edit_url = self.context.createObject(type_name='ATResource')
        if self.request.form:
            edit_url += '?' + urlencode(self.request.form)
            
        self.request.response.redirect(edit_url)
