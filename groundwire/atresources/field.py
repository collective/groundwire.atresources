from zope.component import adapts
from zope.interface import implements
from Acquisition import aq_base
from Products.ATContentTypes.configuration import zconf
from plone.app.blob.field import BlobField
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.blob.scale import BlobImageScaleHandler
from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.blob.config import blobScalesAttr
from groundwire.atresources.interfaces.field import IResourceField

class ResourceField(BlobField, ImageFieldMixin):
    """
    A field for storing resource files.
    """
    
    implements(IResourceField)
    
    swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable
    pil_quality = zconf.pil_config.quality
    pil_resize_algo = zconf.pil_config.resize_algo
    
    def set(self, instance, value, **kwargs):
        """
        Sets the value of the field, resetting image scales.
        """
        
        super(ResourceField, self).set(instance, value, **kwargs)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)
    
    def is_image(self, instance):
        """
        Returns true if this file is an image.
        """
        
        mimetype = self.getContentType(instance)
        if mimetype:
            return mimetype.startswith('image/')
        return False
    
    # Methods from ImageFieldMixin
    def getSize(self, instance, scale=None):
        """
        Get size of scale or original image.
        """
        
        if not self.is_image(instance):
            return None
        return super(ResourceField, self).getSize(instance, scale)

    def getScale(self, instance, scale=None, **kwargs):
        """
        Get scale by name or original.
        """
        
        if not self.is_image(instance):
            return None
        if scale is None:
            return self.getUnwrapped(instance, **kwargs)
        handler = IImageScaleHandler(self, None)
        if handler is not None:
            return handler.getScale(instance, scale)
        return None
        
class ResourceImageScaleHandler(BlobImageScaleHandler):
    """
    Handler for creating and storing scaled version of images in blobs.
    """
    
    adapts(IResourceField)