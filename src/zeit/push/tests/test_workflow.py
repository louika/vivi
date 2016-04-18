from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.push.interfaces import IPushMessages
import lxml.etree
import mock
import zeit.cms.content.interfaces
import zeit.push.testing
import zeit.workflow.testing


class PushServiceProperties(zeit.push.testing.TestCase):

    def test_properties_can_be_set_while_checked_in(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.message_config = [{'type': 'parse'}]
        self.assertEqual([{'type': 'parse'}], push.message_config)

    def test_properties_can_be_set_while_checked_out(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        with checked_out(content) as co:
            push = IPushMessages(co)
            push.message_config = [{'type': 'parse'}]
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        self.assertEqual([{'type': 'parse'}], push.message_config)
        # These DAV properties are not serialized to XML.
        self.assertNotIn('parse', lxml.etree.tostring(
            content.xml, pretty_print=True))


class SendingNotifications(zeit.push.testing.TestCase):

    def setUp(self):
        super(SendingNotifications, self).setUp()
        self.parse = mock.Mock()
        self.zca.patch_adapter(
            self.parse, (zeit.cms.content.interfaces.ICommonMetadata,),
            zeit.push.interfaces.IMessage, name='parse')
        # getAdapter instantiates factory, which causes one call
        self.parse = self.parse()

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_enabled_service_is_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.enabled = True
        push.message_config = [{'type': 'parse', 'enabled': True}]
        self.publish(content)
        self.assertTrue(self.parse.send.called)

    def test_disabled_service_is_not_called(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.enabled = True
        push.message_config = [{'type': 'parse', 'enabled': False}]
        self.publish(content)
        self.assertFalse(self.parse.send.called)

    def test_updates_last_push_date(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.enabled = True
        self.assertEqual(None, push.date_last_pushed)
        self.publish(content)
        self.assertNotEqual(None, push.date_last_pushed)

    def test_error_during_push_is_caught(self):
        self.parse.send.side_effect = RuntimeError('provoked')
        content = ICMSContent('http://xml.zeit.de/testcontent')
        push = IPushMessages(content)
        push.enabled = True
        push.message_config = [{'type': 'parse', 'enabled': True}]
        self.publish(content)
        # This is sort of assertNothingRaised, except that publishing
        # runs in a separate thread (remotetask), so we would not see
        # the exception here anyway.
        self.assertNotEqual(None, push.date_last_pushed)