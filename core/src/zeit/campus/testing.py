from zeit.campus.interfaces import IZCOSection, IZCOFolder
import gocept.httpserverlayer.wsgi
import gocept.selenium
import pkg_resources
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.gallery.testing
import zeit.content.link.testing
import zeit.push.testing
import zope.component
import zope.interface


product_config = """\
<product-config zeit.campus>
  article-stoa-source file://{base}/tests/article-stoa.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.content.article.testing.CONFIG_LAYER,
    zeit.content.link.testing.CONFIG_LAYER,))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,))


class Layer(plone.testing.Layer):

    defaultBases = (PUSH_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['zodbApp']):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            campus = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(campus, IZCOSection)
            zope.interface.alsoProvides(campus, IZCOFolder)
            repository['campus'] = campus


LAYER = Layer()
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER
