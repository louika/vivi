from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import lxml.cssselect
import mock
import transaction
import unittest
import zeit.cms.browser.interfaces
import zeit.content.cp.browser.testing
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zope.component


class TestApplyLayout(zeit.content.cp.testing.SeleniumTestCase):

    def setUp(self):
        super(TestApplyLayout, self).setUp()
        xml_selector = lxml.cssselect.CSSSelector(
            '#lead > .block-inner > .type-teaser').path
        self.teaser_selector = 'xpath=' + xml_selector + '[{pos}]@id'

        self.cp = self.create_and_checkout_centerpage()
        self.cp['lead'].kind = u'major'
        self.cp['lead'].apply_teaser_layouts_automatically = True
        self.cp['lead']._first_teaser_layout = u'leader'
        self.cp['lead'].create_item('teaser')
        self.cp['lead'].create_item('teaser')
        self.cp['lead'].create_item('teaser')
        transaction.commit()
        self.open_centerpage(create_cp=False)

        s = self.selenium
        self.teaser1 = s.getAttribute(self.teaser_selector.format(pos=1))
        self.teaser2 = s.getAttribute(self.teaser_selector.format(pos=2))
        self.teaser3 = s.getAttribute(self.teaser_selector.format(pos=3))

    def wait_for_order(self, order):
        s = self.selenium
        for i, teaser_id in enumerate(order):
            s.waitForAttribute(self.teaser_selector.format(pos=i+1), teaser_id)

    def assert_layout(self, layouts):
        s = self.selenium
        for index, layout in enumerate(layouts):
            id_ = s.getAttribute(self.teaser_selector.format(pos=index+1))
            selector = 'css=#{} > .block-inner > .{}'.format(id_, layout)
            s.assertCssCount(selector, 1)

    def test_moving_first_teaser_overwrites_layout_leader_with_buttons(self):
        s = self.selenium
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(self.teaser1),
            'css=#{} + .landing-zone'.format(self.teaser2),
            '10,10')
        self.wait_for_order([self.teaser2, self.teaser1, self.teaser3])
        self.assert_layout(['buttons', 'buttons', 'buttons'])

    def test_moving_teaser_from_n_to_n_does_not_change_layout(self):
        s = self.selenium
        # set layout of second teaser to 'leader-upright'
        s.click('css=#{} .edit-link'.format(self.teaser2))
        s.waitForVisible('css=.lightbox .leader-upright')
        s.click('css=.lightbox .leader-upright')
        s.waitForCssCount(
            'css=#{} > .block-inner > .leader-upright'.format(self.teaser2), 1)

        # drag from 2nd to 3rd pos
        s.dragAndDropToObject(
            'css=#{} .dragger'.format(self.teaser2),
            'css=#{} + .landing-zone'.format(self.teaser3),
            '10,10')
        self.wait_for_order([self.teaser1, self.teaser3, self.teaser2])
        self.assert_layout(['leader', 'buttons', 'leader-upright'])

    def test_creating_teaser_on_first_position_supersedes_old_leader(self):
        s = self.selenium
        self.assert_layout(['leader', 'buttons', 'buttons'])

        self.create_block('teaser', 'lead')
        s.waitForCssCount('css=#lead .type-teaser', 4)

        self.assert_layout(['leader', 'buttons', 'buttons', 'buttons'])


class TestTeaserDisplay(unittest.TestCase):

    def setUp(self):
        from zeit.content.cp.browser.blocks.teaser import Display
        display = Display()
        display.context = mock.Mock()
        display.request = mock.Mock()
        display.layout = mock.Mock()
        display.url = mock.Mock()
        self.display = display
        self.content = mock.Mock()

    def test_get_image_should_use_preview_when_no_iimages(self):
        with mock.patch('zope.component.queryMultiAdapter') as qma:
            image = self.display.get_image(self.content)
            qma.assert_called_with((self.content, self.display.request),
                                   name='preview')
            self.display.url.assert_called_with(qma())
            self.assertEqual(image, self.display.url())

    def test_get_image_should_not_break_with_no_iimages_and_no_preview(self):
        self.assertTrue(self.display.get_image(self.content) is None)


class CommonEditTest(zeit.content.cp.testing.BrowserTestCase):

    def test_values_are_saved(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open('lead/@@landing-zone-drop'
               '?uniqueId=http://xml.zeit.de/testcontent'
               '&order=top')

        b.open(contents_url)
        b.getLink('Edit block common', index=2).click()
        form_url = b.url

        b.getControl('Title').value = 'foo'
        b.getControl('Apply').click()
        b.open(form_url)
        self.assertEqual('foo', b.getControl('Title').value)


class FunctionalTeaserDisplayTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(FunctionalTeaserDisplayTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)

    def view(self, block):
        view = zeit.content.cp.browser.blocks.teaser.Display()
        view.context = block
        view.request = self.request
        view.update()
        return view

    def create_teaserblock(self, layout):
        container = self.cp.body.create_item('region').create_item('area')
        block = zope.component.getAdapter(
            container, zeit.edit.interfaces.IElementFactory, name='teaser')()
        block.layout = zeit.content.cp.layout.get_layout(layout)
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        for i in range(3):
            id = 't%s' % i
            self.repository[id] = ExampleContentType()
            with zeit.cms.checkout.helper.checked_out(
                    self.repository[id]) as co:
                zeit.content.image.interfaces.IImages(co).image = image
        for i in range(3):
            block.insert(0, self.repository['t%s' % i])
        return block

    def create_article_with_citation(self):
        import zeit.content.article.article
        import zeit.content.article.edit.body
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        citation = body.create_item('citation', 1)
        citation.text = u"Foo"
        return article

    def create_gallery(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.image_folder = self.repository['2007']
        self.repository['2007']['image01'] = ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        transaction.commit()
        gallery.reload_image_folder()
        return gallery

    def test_layout_without_image_pattern_shows_no_header_image(self):
        view = self.view(self.create_teaserblock(layout='short'))
        self.assertEqual(None, view.header_image)

    def test_layout_with_image_pattern_shows_header_image(self):
        view = self.view(self.create_teaserblock(layout='large'))
        self.assertEqual(
            'http://127.0.0.1/repository/2006/DSC00109_2.JPG/@@raw',
            view.header_image)

    def test_shows_list_representation_title_for_non_metadata(self):
        block = self.cp['lead'].create_item('teaser')
        block.insert(0, self.repository['2007'])
        view = self.view(block)
        self.assertEqual('2007', view.teasers[0]['texts'][0]['content'])

    def test_quote_teaser_shows_citation_text_if_article_has_citation(self):
        article = self.create_article_with_citation()
        self.repository['article_with_citation'] = article
        quote_teaserblock = self.create_teaserblock('zar-quote-yellow')
        quote_teaserblock.insert(0, article)
        view = self.view(quote_teaserblock)
        self.assertEqual('Foo', view.teasers[0]['texts'][2][
            'content'])
        self.assertEqual('Zitat:', view.teasers[0]['texts'][1][
            'content'])

    def test_gallery_teaser_forces_mobile_image(self):
        self.repository['gallery'] = self.create_gallery()
        container = self.cp.body.create_item('region').create_item('area')
        block = zope.component.getMultiAdapter(
            (container, self.repository['gallery'], 0),
            zeit.edit.interfaces.IElement)
        assert block.force_mobile_image

    def test_teaser_with_non_quote_layout_shows_teaser_text(
            self):
        article = self.create_article_with_citation()
        article.teaserTitle = 'Bar'
        article.teaserText = 'Baz'
        self.repository['article_with_citation'] = article
        quote_teaserblock = self.create_teaserblock('large')
        quote_teaserblock.insert(0, article)
        view = self.view(quote_teaserblock)
        self.assertEqual('Bar', view.teasers[0]['texts'][1][
            'content'])
        self.assertEqual('Baz', view.teasers[0]['texts'][2][
            'content'])

    def test_quote_teaser_without_quote_in_article_shows_teaser_text(
            self):
        article = zeit.content.article.article.Article()
        article.teaserTitle = 'Bar'
        article.teaserText = 'Baz'
        self.repository['article_with_citation'] = article
        quote_teaserblock = self.create_teaserblock('zar-quote-yellow')
        quote_teaserblock.insert(0, article)
        view = self.view(quote_teaserblock)
        self.assertEqual('Bar', view.teasers[0]['texts'][1][
            'content'])
        self.assertEqual('Baz', view.teasers[0]['texts'][2][
            'content'])
