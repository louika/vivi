import logging
import suds
import suds.cache
import suds.client
import suds.plugin
import suds_ext  # activate monkeypatches
import threading
import urlparse
import zeit.content.author.interfaces
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.cachedescriptors.property
import zope.interface


log = logging.getLogger(__name__)


class CodeFixer(suds.plugin.MessagePlugin):
    """Fix broken XML generated by SUDS.

    Suds generates a duplicate code::

       <ns0:author>
          <ns0:code>dpa</ns0:code>
          <ns0:code>dpa</ns0:code>
       </ns0:author>

    """
    def marshalled(self, context):
        try:
            authors = self.traverse(
                context.envelope,
                'Body', 'newMessageRequest', 'parties', 'authors')
        except ValueError:
            return
        for author in authors.getChildren('author'):
            codes = author.getChildren('code')
            if len(codes) > 1:
                codes[-1].detach()

    def traverse(self, element, *names):
        for name in names:
            element = element.getChild(name)
            if element is None:
                raise ValueError
        return element


class VGWortWebService(object):
    """This class handles the configuration of URL and authentication
    information, and provides better error handling for errors returned by the
    web service.

    Subclasses should override `service_path` to point to the WSDL file, and
    can then call the service's methods on themselves, e. g. if the web service
    provides a method 'orderPixel', call it as self.orderPixel(args).
    """

    # override in subclass
    service_path = None
    namespace = None

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.lock = threading.Lock()

    @zope.cachedescriptors.property.Lazy
    def client(self):
        client = suds.client.Client(
            self.wsdl,
            username=self.username,
            password=self.password,
            # disable caching of the WSDL file, since it leads to intransparent
            # behaviour when debugging.
            # This means it is downloaded afresh every time, but that doesn't
            # occur often, as the utility is instantiated only once, so it's
            # not performance critical other otherwise bad.
            cache=suds.cache.NoCache(),
            plugins=[CodeFixer()])
        return client

    @property
    def wsdl(self):
        return urlparse.urljoin(self.base_url, self.service_path)

    def call(self, method_name, *args, **kw):
        with self.lock:
            try:
                method = getattr(self.client.service, method_name)
                result = method(*args, **kw)
                if isinstance(result, tuple):
                    raise zeit.vgwort.interfaces.TechnicalError(result)
                return result
            except suds.WebFault, e:
                try:
                    message = unicode(e.fault.detail)
                except UnicodeError:
                    message = str(e.fault.detail[0]).decode('latin1')
                if int(getattr(e.fault.detail[0], 'errorcode', 0)) >= 100:
                    raise zeit.vgwort.interfaces.TechnicalError(message)
                else:
                    raise zeit.vgwort.interfaces.WebServiceError(message)

    def create(self, type_):
        return self.client.factory.create('{%s}%s' % (self.namespace, type_))


class PixelService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IPixelService)

    service_path = '/services/1.0/pixelService.wsdl'
    namespace = 'http://vgwort.de/1.0/PixelService/xsd'

    def order_pixels(self, amount):
        result = self.call('orderPixel', amount)
        for pixel in result.pixels.pixel:
            yield (str(pixel._publicIdentificationId),
                   str(pixel._privateIdentificationId))


class MessageService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IMessageService)

    service_path = '/services/1.1/messageService.wsdl'
    namespace = 'http://vgwort.de/1.1/MessageService/xsd'

    def new_document(self, content):
        content = zeit.cms.content.interfaces.ICommonMetadata(
            content, None)
        if content is None:
            raise zeit.vgwort.interfaces.WebServiceError(
                'Artikel existiert nicht mehr.')
        parties = self.create('Parties')
        parties.authors = self.create('Authors')
        if content.authorships:
            ROLES = zeit.content.author.interfaces.ROLE_SOURCE(None)
            for author in content.authorships:
                if not ROLES.report_to_vgwort(author.role):
                    continue
                author = author.target
                if author is None:
                    continue
                involved = self.create('Involved')
                try:
                    if author.vgwortcode:
                        involved.code = author.vgwortcode
                        parties.authors.author.append(involved)
                    elif (author.firstname and author.lastname and
                            author.firstname.strip() and
                            author.lastname.strip()):
                        involved.firstName = author.firstname
                        involved.surName = author.lastname
                        if author.vgwortid:
                            involved.cardNumber = author.vgwortid
                        parties.authors.author.append(involved)
                except AttributeError:
                    log.error('Could not report %s', content, exc_info=True)
        else:
            # Report the freetext authors if no structured authors are
            # available. VGWort will do some matching then.
            for author in content.authors:
                author = author.strip().split()
                if len(author) < 2:
                    # Need at least one space to split firstname and lastname
                    continue
                involved = self.create('Involved')
                involved.firstName = ' '.join(author[:-1])
                involved.surName = author[-1]
                parties.authors.author.append(involved)

        for author in content.agencies:
            involved = self.create('Involved')
            try:
                if not author.vgwortcode:
                    continue
                involved.code = author.vgwortcode
                parties.authors.author.append(involved)
            except AttributeError:
                log.warning('Ignoring agencies for %s', content, exc_info=True)

        # BBB for articles created by zeit.newsimport before `agencies` existed
        if content.product and content.product.vgwortcode:
            involved = self.create('Involved')
            involved.code = content.product.vgwortcode
            parties.authors.author.append(involved)

        if not parties.authors.author:
            raise zeit.vgwort.interfaces.WebServiceError(
                'Kein Autor mit VG-Wort-Code gefunden.')

        text = self.create('MessageText')
        text.text = self.create('Text')
        text._lyric = False
        text.shorttext = content.title[:100]
        searchable = zope.index.text.interfaces.ISearchableText(content)
        text.text.plainText = u'\n'.join(
            searchable.getSearchableText()).encode('utf-8').encode('base64')

        ranges = self.create('Webranges')
        url = self.create('Webrange')
        url.url = content.uniqueId.replace(
            'http://xml.zeit.de', 'http://www.zeit.de') + '/komplettansicht'
        ranges.webrange.append(url)

        token = zeit.vgwort.interfaces.IToken(content)
        self.call('newMessage', parties, text, ranges,
                  privateidentificationid=token.private_token)


def service_factory(TYPE):
    def factory():
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.vgwort')
        return TYPE(config['vgwort-url'],
                    config['username'],
                    config['password'])
    factory = zope.interface.implementer(
        list(zope.interface.implementedBy(TYPE))[0])(factory)
    return factory

real_pixel_service = service_factory(PixelService)
real_message_service = service_factory(MessageService)
