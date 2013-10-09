from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface import file as atfile
from Products.ATContentTypes.interface import image as atimage

# support for zope2-interfaces
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage


interfaces = {
    'File': [atfile.IATFile, atfile.IFileContent],
    'Image': [atimage.IATImage, atimage.IImageContent],
}

z2interfaces = {
    'File': [Z2IATFile],
    'Image': [Z2IATImage],
}


def markAs(obj, typename):
    for i in interfaces.get(typename, ()):
        alsoProvides(obj, i)
    z2 = z2interfaces.get(typename, None)
    if z2 is not None:
        implements = getattr(obj, '__implements__', [])
        obj.__implements__ = tuple(set(implements).union(z2))


def unmarkAs(obj, typename):
    for i in interfaces.get(typename, ()):
        noLongerProvides(obj, i)
    z2 = z2interfaces.get(typename, None)
    if z2 is not None:
        implements = getattr(obj, '__implements__', [])
        obj.__implements__ = tuple(set(implements) - set(z2))