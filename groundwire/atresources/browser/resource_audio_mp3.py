from zope.publisher.browser import BrowserPage
from zope.app.component.hooks import getSite
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from groundwire.atresources.utils import json_serialize
import time

class MP3(BrowserPage):
    """
    A view to display an MP3 audio file.
    """
    
    __call__ = ViewPageTemplateFile('resource_audio_mp3.pt')
    
    def resource_js(self):
        """
        Returns javascript to be inserted in the head of the resource template.
        """
        
        portal_url = getSite().absolute_url()
        
        return """
        <script type="text/javascript" src="%s/++resource++swfobject.js"></script>
        <script type="text/javascript" src="%s/++resource++audio_player.js"></script>  
        <script type="text/javascript">  
            AudioPlayer.setup("%s/++resource++audio_player.swf", {  
                width: 300
            });  
        </script>
        """ % (portal_url, portal_url, portal_url)
    
    @memoize
    def player_id(self):
        """
        Returns the vimeo ID of the movie.
        """
        
        return 'audio-player-%s' % hash((time.time(),))
        
    def player_options(self):
        """
        Returns the json object containing the player options.
        """
        
        return json_serialize({
            'soundFile': '%s/at_download/file' % self.context.absolute_url(),
        })
        
        
        

