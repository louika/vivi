import json
import mock
import urllib2
import zeit.cms.interfaces
import zeit.retresco.testing
import zope.testbrowser.testing


class TMSUpdateRequestTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_endpoint_avoids_get(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 405: Method Not Allowed'):
            b.open('http://localhost/@@update_keywords')

    def test_endpoint_rejects_post_without_doc_ids(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords', '')
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords',
                   '{"foo" : "bar"}', 'application/x-javascript')

    def test_endpoint_creates_async_job(self):
        b = zope.testbrowser.testing.Browser()
        with mock.patch('zeit.retresco.update.index') as index:
            b.post('http://localhost/@@update_keywords',
                   '{"doc_ids" : ['
                   '"{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}", '
                   '"{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}"]}',
                   'application/x-javascript')
            self.assertEquals({'message': 'OK'}, json.loads(b.contents))
            self.assertEquals('200 Ok', b.headers.getheader('status'))

            with zeit.cms.testing.site(self.getRootFolder()):
                self.assertEqual(2, index.call_count)
                self.assertEqual(
                    zeit.cms.interfaces.ICMSContent(
                        'http://xml.zeit.de/online/2007/01/Somalia'),
                    index.call_args[0][0])
                self.assertEqual(
                    {'enrich': True, 'publish': True},
                    index.call_args[1])