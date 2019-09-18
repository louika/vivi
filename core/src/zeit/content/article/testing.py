import gocept.httpserverlayer.wsgi
import gocept.selenium
import pkg_resources
import plone.testing
import re
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.author.testing
import zeit.content.gallery.testing
import zeit.content.volume.testing
import zeit.push.testing
import zope.component


product_config = """
<product-config zeit.content.article>
  book-recension-categories file://{base}/tests/recension_categories.xml
  genre-url file://{base}/tests/article-genres.xml
  image-display-mode-source file://{base}/edit/tests/image-display-modes.xml
  legacy-display-mode-source file://{base}/edit/tests/legacy-display-modes.xml
  image-variant-name-source file://{base}/edit/tests/image-variant-names.xml
  legacy-variant-name-source file://{base}/edit/tests/legacy-variant-names.xml
  video-layout-source file://{base}/edit/tests/video-layouts.xml
  infobox-layout-source file://{base}/edit/tests/infobox-layouts.xml
  template-source file://{base}/edit/tests/templates.xml
  header-module-source file://{base}/edit/tests/header-modules.xml
  citation-layout-source file://{base}/edit/tests/citation-layouts.xml
  box-layout-source file://{base}/edit/tests/box-layouts.xml
  puzzleforms-source file://{base}/edit/tests/puzzleforms.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, ''))


checker = zeit.cms.testing.OutputChecker([
    (re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>")])
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(product_config, bases=(
    zeit.content.author.testing.CONFIG_LAYER,
    zeit.content.gallery.testing.CONFIG_LAYER,
    zeit.content.volume.testing.CONFIG_LAYER))
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))

PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZOPE_LAYER,))
EMBED_LAYER = zeit.content.modules.testing.EmbedTemplateLayer(
    name='EmbedTemplateLayer', bases=(ZOPE_LAYER,))
TEMPLATE_LAYER = plone.testing.Layer(
    name='Layer', bases=(PUSH_LAYER, EMBED_LAYER))


class ArticleLayer(plone.testing.Layer):

    defaultBases = (TEMPLATE_LAYER,)

    def testSetUp(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        prop = connector._get_properties(
            'http://xml.zeit.de/online/2007/01/Somalia')
        prop[zeit.cms.tagging.testing.KEYWORD_PROPERTY] = (
            'testtag|testtag2|testtag3')


LAYER = ArticleLayer()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase,
                         zeit.cms.tagging.testing.TaggingHelper):

    layer = LAYER

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.setup_tags('testtag', 'testtag2', 'testtag3')

    def get_article(self):

        wl = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        article = create_article()
        article.keywords = [
            wl.get(tag) for tag in ('testtag', 'testtag2', 'testtag3')]
        return article

    def get_factory(self, article, factory_name):
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        return zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, factory_name)


def create_article():
    from zeit.content.article.article import Article
    from zeit.content.article.interfaces import IArticle
    import zeit.cms.browser.form
    article = Article()
    zeit.cms.browser.form.apply_default_values(article, IArticle)
    article.year = 2011
    article.title = u'title'
    article.ressort = u'Deutschland'
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
    return article


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):

    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER

    WIDGET_SELECTOR = 'xpath=//label[@for="%s"]/../../*[@class="widget"]'

    def assert_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.assertText(path, text)

    def wait_for_widget_text(self, widget_id, text):
        path = self.WIDGET_SELECTOR % widget_id
        self.selenium.waitForElementPresent(path)
        self.selenium.waitForText(path, text)
