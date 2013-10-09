from zope.interface import implements
from zope.component import getAdapters
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from Products.ATContentTypes.content.file import ATFile
from Products.MimetypesRegistry.common import MimeTypeException
from plone.app.imaging.interfaces import IImageScaleHandler
from logging import getLogger
from groundwire.atresources import atresourcesMessageFactory as _
from groundwire.atresources.interfaces import IATResource
from groundwire.atresources.interfaces.atresource import IResourceMimeTypeProvider
from groundwire.atresources.config import PROJECTNAME
from groundwire.atresources.field import ResourceField
from groundwire.atresources.markings import markAs, unmarkAs

try:
    from plone.app.blob.utils import openBlob
except ImportError:
    def openBlob(blob, mode='r'):
        """ open a blob taking into consideration that it might need to be
            invalidated in order to be fetch again via zeo;  please see
            http://dev.plone.org/plone/changeset/32170/ for more info """
        try:
            return blob.open(mode)
        except IOError:
            blob._p_deactivate()
            return blob.open(mode)

DocumentSchema = document.ATDocumentSchema.copy()
DocumentSchema['text'].primary = False

ATResourceSchema = \
    DocumentSchema + \
    atapi.Schema((

    ResourceField('file',
        primary=True,
        required=False,
        searchable=True,
        index_method='getIndexValue',
        validators = ('isNonEmptyFile', 'checkFileMaxSize',),
        widget = atapi.FileWidget(
            label=_(u'File'),
            description=_(u'Upload the resource file or provide the URL below.'),
            show_content_type = False,
        ),
    ),
    
    atapi.StringField('url',
        required=False,
        widget=atapi.StringWidget(
            label=_(u"URL"),
            description=_(u'For resources hosted elsewhere (e.g. YouTube), \
                enter the full URL of the resource.'),
            size=50,
        ),
    ),

))

schemata.finalizeATCTSchema(ATResourceSchema, moveDiscussion=False)

def image_only(func):
    """
    Decorator that only calls the function if the file in file is
    an image. Otherwise it returns None.
    """
    def check_image(instance, *args, **kwargs):
        if instance.getField('file').is_image(instance):
            return func(instance, *args, **kwargs)
        return None
    # We need to preserve the docstring of the original function because Zope
    # uses it to determine acquisition. If we had Python 2.5, we could do this
    # using the functools @wrap decorator.
    if hasattr(func, '__doc__'):
        check_image.__doc__ = func.__doc__
    return check_image
    
def file_or_super(func):
    """
    Decorator that only calls the function if a file is set. Otherwise,
    it calls the same function on the superclass.
    """
    def check_file(instance, *args, **kwargs):
        if instance.getField('file').getFilename(instance):
            return func(instance, *args, **kwargs)
        return getattr(super(instance.__class__, instance), func.__name__)(*args, **kwargs)
    # We need to preserve the docstring of the original function because Zope
    # uses it to determine acquisition. If we had Python 2.5, we could do this
    # using the functools @wrap decorator.
    if hasattr(func, '__doc__'):
        check_file.__doc__ = func.__doc__
    return check_file

class ATResource(ATCTFileContent, ATCTImageTransform, document.ATDocument):
    """A resource file."""
    implements(IATResource)

    meta_type = "ATResource"
    schema = ATResourceSchema
    
    security = ClassSecurityInfo()
    
    security.declarePrivate('post_validate')
    def post_validate(self, REQUEST, errors):
        """
        Validates the form to make sure that there is either a file or a URL
        but not both.
        """
        
        form = REQUEST.form
        url = form.get('url', None)
        file_delete = form.get('file_delete', None)
        file_file = form.get('file_file', None)
        current_filename = self.getField('file').getFilename(self)
        has_file = (file_file and file_file.filename) or \
            (current_filename and not file_delete == 'delete')
        
        if not url and not has_file:
            errors['file'] = errors['url'] = \
                _('Please choose a file to upload or provide a resource URL.')
            
        if url and has_file:
            errors['file'] = errors['url'] = \
                _('Resources cannot contain both a file and a URL.')
        
        super(ATResource, self).post_validate(REQUEST, errors)
    
    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """
        Download the file inline or as an attachment.
        """
        
        field = self.getPrimaryField()
        if field.getFilename(self):
            if field.is_image(self) or field.getContentType(self) in ATFile.inlineMimetypes:
                return field.index_html(self, REQUEST, RESPONSE)
            else:
                return field.download(self, REQUEST, RESPONSE)
        elif self.getUrl():
            return RESPONSE.redirect(self.getUrl())
            
    def setFile(self, value, **kwargs):
        """
        Set the file, giving the resource object the appropriate interfaces.
        """
        
        file_field = self.getField('file')
        file_field.set(self, value, **kwargs)
        
        unmarkAs(self, 'File')
        unmarkAs(self, 'Image')
        
        if file_field.is_image(self):
            markAs(self, 'Image')
        elif file_field.getFilename(self):
            markAs(self, 'File')
            
    def resource_mimetype(self):
        """
        Returns the mimetype for the resource file or URL.
        """
        
        if self.getFile().filename:
            return self.file.getContentType()
        
        elif self.getUrl():
            parsers = getAdapters((self,), IResourceMimeTypeProvider)
            for parser in parsers:
                mimetype = parser[1].mimetype()
                if mimetype:
                    return mimetype
            return 'url/default'
            
        return None
    
    # ATFile replacement
    security.declareProtected(View, 'get_data')
    @file_or_super
    def get_data(self):
        """
        Returns the data as a string.
        """
        
        return str(self.getFile())

    data = ComputedAttribute(get_data, 1)
    
    @file_or_super
    def __str__(self):
        """
        Returns the data as a string.
        """
        
        if self.getPrimaryField().is_image(self):
            return self.getPrimaryField().tag(self)
        else:
            return self.get_data()

    @file_or_super
    def __repr__(self):
        """
        Mimics the the old file and image types from ATCT for improved
        test compatibility
        """
        
        res = super(ATResource, self).__repr__()
        if self.getPrimaryField().is_image(self):
            return res.replace(ATResource.__name__, 'ATImage', 1)
        else:
            return res.replace(ATResource.__name__, 'ATFile', 1)

    security.declareProtected(ModifyPortalContent, 'setFilename')
    def setFilename(self, value, key=None):
        """
        Convenience method to set the file name on the field.
        """
        
        self.getFile().setFilename(value)

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        """
        Convenience method to set the mime-type.
        """
        
        self.getFile().setContentType(value)

    security.declarePublic('getIcon')
    @file_or_super
    def getIcon(self, relative_to_portal=False):
        """
        Calculates an icon based on mime-type.
        """
        
        contenttype = self.getFile().getContentType()
        mtr = getToolByName(self, 'mimetypes_registry', None)
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException:
            mimetypeitem = None
        if mimetypeitem is None or mimetypeitem == ():
            return super(ATResource, self).getIcon(relative_to_portal)
        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName(self, 'portal_url')
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None, **kwargs):
        # implement cmf_edit for image and file distinctly
        if file is not None:
            self.setFile(file)
        if title is not None:
            self.setTitle(title)
        if kwargs:
            self.edit(**kwargs)
        else:
            self.reindexObject()

    # ATImage replacement
    security.declareProtected(View, 'getImage')
    @image_only
    def getImage(self, **kwargs):
        """
        Gets the image.
        """
        
        return self.getFile()

    security.declareProtected(ModifyPortalContent, 'setImage')
    def setImage(self, value, **kwargs):
        """
        Sets the image.
        """
        
        self.setFile(value, **kwargs)
    
    security.declareProtected(View, 'tag')
    @image_only
    def tag(self, **kwargs):
        """
        Generates image tag using the API of the ImageField.
        """
        
        return self.getField('file').tag(self, **kwargs)

    security.declareProtected(View, 'getSize')
    @image_only
    def getSize(self, scale=None):
        field = self.getField('file')
        if field is not None:
            return field.getSize(self, scale=scale)

    security.declareProtected(View, 'getWidth')
    @image_only
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(View, 'getHeight')
    @image_only
    def getHeight(self, scale=None):
        return self.getSize(scale)[1]

    width = ComputedAttribute(getWidth, 1)
    height = ComputedAttribute(getHeight, 1)
    
    @file_or_super
    def __bobo_traverse__(self, REQUEST, name):
        """
        Helper to access image scales the old way during
        unrestrictedTraverse calls.
        """
        
        if isinstance(REQUEST, dict):
            if '_' in name:
                fieldname, scale = name.split('_', 1)
            else:
                fieldname, scale = name, None
            field = self.getField(fieldname)
            handler = IImageScaleHandler(field, None)
            if handler is not None:
                image = handler.getScale(self, scale)
                if image is not None:
                    return image
        return super(ATResource, self).__bobo_traverse__(REQUEST, name)
    
    # ATCTImageTransform
    security.declarePrivate('getImageAsFile')
    @image_only
    def getImageAsFile(self, img=None, scale=None):
        """
        Gets the image as file-like object.
        """
        if img is None:
            field = self.getField('file')
            img = field.getScale(self, scale)
        return openBlob(self.getFile().getBlob())

    # Index accessor using portal transforms to provide index data
    security.declarePrivate('getIndexValue')
    def getIndexValue(self, mimetype='text/plain'):
        """
        Indexes the file content.
        """
        
        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')
        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)

atapi.registerType(ATResource, PROJECTNAME)
