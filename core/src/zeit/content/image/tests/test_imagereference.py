# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.content.reference import ReferenceProperty
from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.content.image.interfaces import IImageMetadata
import gocept.async.tests
import lxml.etree
import mock
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.content.image.testing
import zope.copypastemove.interfaces


class ImageAssetTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_IImages_accepts_IImage_for_backwards_compatibility(self):
        with self.assertNothingRaised():
            zeit.content.image.interfaces.IImages['image'].validate(
                ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG'))


class ImageReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(ImageReferenceTest, self).setUp()
        TestContentType.images = ReferenceProperty('.body.image', 'image')

    def tearDown(self):
        del TestContentType.images
        super(ImageReferenceTest, self).tearDown()

    def test_local_values_override_original_ones(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        ref.title = u'localtitle'
        ref.caption = u'localcaption'
        self.assertEqual('localtitle', ref.xml.get('title'))
        self.assertEqual('localcaption', ref.xml.bu)

        ref.update_metadata()
        self.assertEqual('localtitle', ref.xml.get('title'))
        self.assertEqual('localcaption', ref.xml.bu)

    def test_empty_local_values_leave_original_ones_alone(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image) as co:
            IImageMetadata(co).title = 'originaltitle'
            IImageMetadata(co).caption = 'originalcaption'
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        self.assertEqual('originaltitle', ref.xml.get('title'))
        self.assertEqual('originalcaption', ref.xml.bu)
        ref.update_metadata()
        self.assertEqual('originaltitle', ref.xml.get('title'))
        self.assertEqual('originalcaption', ref.xml.bu)

    def test_setting_local_value_none_yields_none(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = self.repository['testcontent']
        ref = content.images.create(image)
        content.images = (ref,)
        ref.title = u'localtitle'
        ref.caption = u'localcaption'
        self.assertEqual('localtitle', ref.title)
        self.assertEqual('localcaption', ref.caption)
        ref.title = None
        ref.caption = u''  # the caption field is non-None
        self.assertEqual(None, ref.title)
        self.assertEqual('', ref.caption)

    def test_updater_suppress_errors(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        content = ICheckoutManager(self.repository['testcontent']).checkout()
        zeit.content.image.interfaces.IImages(content).image = image

        # This error condition cannot be synthesized easily (would need to make
        # an ImageGroup lose its metadata so it's treated as a Folder), and
        # even mocking it is rather complicated, sigh.
        def mock_query(*args, **kw):
            if kw.get('name') == 'image':
                return None
            return queryAdapter(*args, **kw)
        queryAdapter = zope.component.queryAdapter

        with mock.patch('zope.component.queryAdapter', mock_query):
            with self.assertNothingRaised():
                updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                    content)
                updater.update(content.xml, suppress_errors=True)


class MoveReferencesTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_moving_image_updates_uniqueId_in_referencing_obj(self):
        # This is basically the same test as zeit.cms.redirect.tests.test_move,
        # but for image references instead of related references.
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(self.repository['testcontent']) as co:
            zeit.content.image.interfaces.IImages(co).image = image

        zope.copypastemove.interfaces.IObjectMover(image).moveTo(
            self.repository, 'changed')
        gocept.async.tests.process()

        content = self.repository['testcontent']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                'http://xml.zeit.de/changed',
                zeit.content.image.interfaces.IImages(content).image.uniqueId)
            self.assertFalse(lookup().find.called)
        self.assertIn(
            'http://xml.zeit.de/changed',
            lxml.etree.tostring(content.xml, pretty_print=True))
