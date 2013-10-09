from groundwire.atresources.browser.resource_audio_mp3 import MP3
from groundwire.atresources.utils import json_serialize

class MP3URL(MP3):
    """
    A view to display an MP3 audio URL.
    """
        
    def player_options(self):
        """
        Returns the json object containing the player options.
        """
        
        url = self.context.getUrl().strip()
        return json_serialize({
            'soundFile': url,
        })