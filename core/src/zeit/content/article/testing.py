# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import re
import shutil
import tempfile
import zeit.brightcove.testing
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.solr.testing
import zope.app.testing.functional
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.article>
    cds-import-valid-path $$ressort/$$year/$$volume
    cds-import-invalid-path cds/invalid/$$year/$$volume
</product-config>
"""


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),])
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


ArticleLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        product_config +
        zeit.content.cp.testing.product_config +
        zeit.brightcove.testing.product_config +
        zeit.solr.testing.product_config +
        zeit.cms.testing.cms_product_config))


class TestBrowserLayer(ArticleLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        ArticleLayer.setup.setUp()

    @classmethod
    def testTearDown(cls):
        ArticleLayer.setup.tearDown()


class ArticleBrightcoveLayer(TestBrowserLayer,
                             zeit.brightcove.testing.BrightcoveHTTPLayer,
                             zeit.solr.testing.SolrMockLayerBase):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        zeit.brightcove.testing.update_repository(
            ArticleLayer.setup.getRootFolder())

    @classmethod
    def testTearDown(cls):
        pass


CDSZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'cds_ftesting.zcml',
    product_config=(
        product_config +
        zeit.content.cp.testing.product_config +
        zeit.cms.testing.cms_product_config))


class CDSLayer(CDSZCMLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        product_config['cds-export'] = tempfile.mkdtemp()
        product_config['cds-import'] = tempfile.mkdtemp()

    @classmethod
    def testTearDown(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        # I don't know why, but those directories get removed automatically
        # somehow. 
        try:
            shutil.rmtree(product_config['cds-export'])
        except OSError:
            pass
        try:
            shutil.rmtree(product_config['cds-import'])
        except OSError:
            pass
        del product_config['cds-export']
        del product_config['cds-import']


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ArticleLayer


selenium_layer = gocept.selenium.ztk.Layer(ArticleLayer)


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = selenium_layer
    skin = 'vivi'


class BrowserAssertions(object):

    def assert_ellipsis(self, want, got=None):
        import difflib
        import doctest
        if got is None:
            got = self.browser.contents
        # normalize whitespace
        norm_want = ' '.join(want.split())
        norm_got = ' '.join(got.split())
        if doctest._ellipsis_match(norm_want, norm_got):
            return True
        # Report ndiff
        engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
        diff = list(engine.compare(want.splitlines(True),
                                   got.splitlines(True)))
        kind = 'ndiff with -expected +actual'
        diff = [line.rstrip() + '\n' for line in diff]
        self.fail('Differences (%s):\n' % kind + ''.join(diff))

    def assert_json(self, want, got=None):
        import doctest
        import simplejson
        if got is None:
            got = self.browser.contents
        data = simplejson.loads(got)
        self.assertEqual(want, data)
        return data
