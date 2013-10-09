from zope.publisher.browser import BrowserPage
from zope.app.component.hooks import getSite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from StringIO import StringIO
import hexagonit.swfheader
import time

class Flash(BrowserPage):
    """
    A view to display a Flash movie.
    """
    
    __call__ = ViewPageTemplateFile('resource_application_x-shockwave-flash.pt')
    
    def resource_js(self):
        """
        Returns javascript to be inserted in the head of the resource template.
        """
        
        portal_url = getSite().absolute_url()
        
        return """
        <script type="text/javascript" src="%s/++resource++swfobject.js"></script>
        <script type="text/javascript">
            swfobject.embedSWF(%s);
        </script>
        """ % (portal_url, self.player_options())
    
    @memoize
    def player_id(self):
        """
        Returns the flash player.
        """
        
        return 'flash-%s' % hash((time.time(),))
        
    def player_options(self):
        """
        Returns the json object containing the player options.
        """
        
        flash_content = StringIO(self.context.getFile())
        metadata = hexagonit.swfheader.parse(flash_content)
        
        options = [
            '%s' % self.context.absolute_url(),
            self.player_id(),
            str(metadata['width']),
            str(metadata['height']),
            str(metadata['version']),
        ]
        
        return ','.join(['"%s"' % option for option in options])
        

