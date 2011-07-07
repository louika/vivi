# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import UserDict
import gocept.lxml.interfaces
import grokcore.component as grok
import pkg_resources
import zeit.cms.content.xmlsupport
import zeit.cms.type
import zeit.edit.container
import zeit.newsletter.interfaces
import zope.interface


BODY_NAME = 'newsletter_body'


class Newsletter(zeit.cms.content.xmlsupport.XMLContentBase,
                 UserDict.DictMixin):

    zope.interface.implements(zeit.newsletter.interfaces.INewsletter)

    default_template = pkg_resources.resource_string(__name__, 'template.xml')

    subject = zeit.cms.content.property.ObjectPathProperty(
        '.head.subject', zeit.newsletter.interfaces.INewsletter['subject'])

    def keys(self):
        return [BODY_NAME]

    def __getitem__(self, key):
        if key == BODY_NAME:
            area = zope.component.getMultiAdapter(
                (self, self.xml.body),
                zeit.edit.interfaces.IArea,
                name=key)
            return zope.container.contained.contained(area, self, key)
        raise KeyError(key)

    def send(self):
        pass # nyi, see #9138

    def send_test(self, to):
        pass # nyi, see #9138


class NewsletterType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Newsletter
    interface = zeit.newsletter.interfaces.INewsletter
    type = 'newsletter'
    title = _('Daily Newsletter') # multiple categories are not supported yet


class Body(zeit.edit.container.TypeOnAttributeContainer,
           grok.MultiAdapter):

    __name__ = BODY_NAME

    grok.implements(zeit.newsletter.interfaces.IBody)
    grok.provides(zeit.newsletter.interfaces.IBody)
    grok.adapts(
        zeit.newsletter.interfaces.INewsletter,
        gocept.lxml.interfaces.IObjectified)
    grok.name(BODY_NAME)


class Group(zeit.edit.container.TypeOnAttributeContainer,
            grok.MultiAdapter):

    grok.implements(zeit.newsletter.interfaces.IGroup)
    grok.provides(zeit.newsletter.interfaces.IGroup)
    grok.adapts(
        zeit.newsletter.interfaces.IBody,
        gocept.lxml.interfaces.IObjectified)
    grok.name('group')

    title = zeit.cms.content.property.ObjectPathProperty(
        '.head.title', zeit.newsletter.interfaces.IGroup['title'])


zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IBody, 'group', _('Group'),
    tag_name='region')


class Teaser(zeit.edit.block.SimpleElement):

    area = zeit.newsletter.interfaces.IGroup
    grok.implements(zeit.newsletter.interfaces.ITeaser)
    type = 'teaser'

    reference = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))


zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IGroup, 'teaser', _('Teaser'))
