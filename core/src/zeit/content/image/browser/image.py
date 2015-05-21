from zeit.cms.i18n import MessageFactory as _
from zope.browserpage import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy as cachedproperty
import PIL.Image
import pkg_resources
import random
import transaction
import z3c.conditionalviews
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.cms.settings.interfaces
import zeit.connector.interfaces
import zeit.content.image.imagereference
import zeit.content.image.interfaces
import zope.component
import zope.file.download
import zope.publisher.interfaces


def get_img_tag(image, request, view=None):
    """Render <img.../>-tag."""
    url = zope.component.getMultiAdapter(
        (image, request), name='absolute_url')
    width, height = image.getImageSize()
    if view:
        view = '/' + view
    else:
        view = ''
    return (
        '<img src="%s%s" alt="" height="%s" width="%s" border="0" />' % (
            url, view, height, width))


class Image(zope.file.download.Display):

    def __call__(self):
        self.request.response.setHeader('Content-Type', self.context.mimeType)
        return self.stream_image()

    @z3c.conditionalviews.ConditionalView
    def stream_image(self):
        return super(Image, self).__call__()


class ImageView(zeit.cms.browser.view.Base):

    title = _('View image')

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)

    def tag(self):
        return get_img_tag(self.context, self.request, view='@@raw')

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]

    @property
    def copyrights(self):
        result = []
        for copyright, url, nofollow in self.metadata.copyrights:
            result.append(dict(
                copyright=copyright,
                url=url,
                nofollow=nofollow))
        return result


class ReferenceDetailsHeading(zeit.cms.browser.objectdetails.Details):

    template = ViewPageTemplateFile(pkg_resources.resource_filename(
        'zeit.cms.browser', 'object-details-heading.pt'))

    def __init__(self, context, request):
        super(ReferenceDetailsHeading, self).__init__(context.target, request)

    def __call__(self):
        return self.template()


class ReferenceDetailsBody(ImageView):

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(
            self.context.target)

    def tag(self):
        return get_img_tag(self.context.target, self.request, view='@@raw')


class Scaled(object):

    filter = PIL.Image.ANTIALIAS

    def __call__(self):
        return self.scaled()

    def tag(self):
        return get_img_tag(self.scaled.context, self.request)

    @cachedproperty
    def scaled(self):
        try:
            image = zeit.content.image.interfaces.ITransform(self.context)
        except TypeError:
            image = self.context
        else:
            image = image.thumbnail(self.width, self.height, self.filter)
            image.__name__ = self.__name__

            def cleanup(commited, image):
                # Releasing the last reference triggers the weakref cleanup of
                # ZODB.blob.Blob, since this local_data Blob never was part of
                # a ZODB connection, which will delete the temporary file.
                image.local_data = None
            transaction.get().addAfterCommitHook(cleanup, [image])
        image_view = zope.component.getMultiAdapter(
            (image, self.request), name='raw')
        return image_view


class Preview(Scaled):

    width = 500
    height = 500


class MetadataPreview(Scaled):

    width = 500
    height = 90


class Thumbnail(Scaled):

    width = height = 100


class Random(object):
    """Temporary non-production ready view for Variant prototype.

    Please remove as soon as possible. :P

    """

    filter = PIL.Image.ANTIALIAS

    def __call__(self):
        return self.scaled()

    def tag(self):
        return get_img_tag(self.scaled.context, self.request)

    @cachedproperty
    def scaled(self):
        dx = random.randint(0, 200)
        dy = random.randint(0, 200)
        image = zeit.imp.interfaces.ICropper(self.context).crop(
            500, 500, dx, dy, dx + 300, dy + 300)
        transform = zeit.content.image.interfaces.ITransform(self.context)
        image = transform._construct_image(image)
        image.__name__ = self.__name__

        def cleanup(commited, image):
            # Releasing the last reference triggers the weakref cleanup of
            # ZODB.blob.Blob, since this local_data Blob never was part of
            # a ZODB connection, which will delete the temporary file.
            image.local_data = None
        transaction.get().addAfterCommitHook(cleanup, [image])
        image_view = zope.component.getMultiAdapter(
            (image, self.request), name='raw')
        return image_view


class ImageListRepresentation(
    zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing article content resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.content.image.interfaces.IImage,
                          zope.publisher.interfaces.IPublicationRequest)

    author = ressort = page = u''

    @property
    def title(self):
        title = self.image_metadata.title
        if not title:
            title = self.context.__name__
        return title

    @property
    def volume(self):
        return self.image_metadata.volume

    @property
    def year(self):
        return self.image_metadata.year

    @property
    def searchableText(self):
        # XXX
        return ''

    @cachedproperty
    def image_metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.content.image.interfaces.IImageSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def imagefolder_browse_location(context, source):
    """The image browse location is deduced from the current folder, i.e.

        for /online/2007/32 it is /bilder/2007/32

    """
    unique_id = context.uniqueId
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    base = image_folder = None
    try:
        obj_in_repository = repository.getContent(unique_id)
    except KeyError:
        pass
    else:
        # Try to get a base folder
        while base is None:
            properties = zeit.connector.interfaces.IWebDAVProperties(
                obj_in_repository, None)
            if properties is None:
                break
            base = properties.get(('base-folder',
                                   'http://namespaces.zeit.de/CMS/Image'))
            obj_in_repository = obj_in_repository.__parent__

    if base is not None:
        try:
            base_obj = repository.getContent(base)
        except KeyError:
            pass
        else:
            # Get from the base folder to the year/volume folder
            settings = zeit.cms.settings.interfaces.IGlobalSettings(context)
            try:
                image_folder = base_obj[
                    '%04d' % settings.default_year][
                    '%02d' % settings.default_volume]
            except KeyError:
                pass

    if image_folder is None:
        all_content_source = zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
        image_folder = zope.component.queryMultiAdapter(
            (context, all_content_source),
            zeit.cms.browser.interfaces.IDefaultBrowsingLocation)

    return image_folder


@zope.component.adapter(
    zeit.content.image.imagereference.ImagesAdapter,
    zeit.content.image.interfaces.IImageSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def imageadapter_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class MetadataPreviewHTML(object):

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)
