# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import copy
import htmlentitydefs
import StringIO

import lxml.etree
import gocept.lxml.objectify

import persistent
import rwproperty

import zope.component
import zope.interface
import zope.security.proxy

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.wysiwyg.interfaces

import zeit.content.article.interfaces
import zeit.content.article.syndication


ARTICLE_NS = zeit.content.article.interfaces.ARTICLE_NS
ARTICLE_TEMPLATE = """\
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
</article>"""


class Article(zeit.cms.content.metadata.CommonMetadata):
    """Article is the main content type in the Zeit CMS."""

    zope.interface.implements(
        zeit.content.article.interfaces.IArticle,
        zeit.wysiwyg.interfaces.IHTMLContent,
        zeit.cms.content.interfaces.IDAVPropertiesInXML)

    default_template = ARTICLE_TEMPLATE

    textLength = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['textLength'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'text-length')
    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['commentsAllowed'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comments')
    boxMostRead = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['boxMostRead'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'mostread')
    pageBreak = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['pageBreak'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'paragraphsperpage')
    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['dailyNewsletter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')
    automaticTeaserSyndication = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['automaticTeaserSyndication'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'automaticTeaserSyndication',
        use_default=True)
    syndicatedIn = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['syndicatedIn'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'syndicatedIn',
        use_default=True)

    #banner = zeit.cms.content.property.AttributeProperty(
    #    zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'banner')
    #syndicatedIn = zeit.cms.content.property.ResourceSet(
    #    zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'syndicatedIn')
    #automaticTeaserSyndication = zeit.cms.content.property.ResourceSet(
    #    zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'automaticTeaserSyndication')
    syndicationLog = zeit.content.article.syndication.SyndicationLogProperty()

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'banner'))


    @rwproperty.getproperty
    def html(self):
        """return html snippet of article."""
        html = []
        for node in self._html_getnodes():
            # Copy all nodes. This magically removes namespace declarations.
            node = copy.copy(node)
            if node.tag == 'intertitle':
                node.tag = 'h3'
            html.append(lxml.etree.tostring(
                node, pretty_print=True, encoding=unicode))
        return '\n'.join(html)


    @rwproperty.setproperty
    def html(self, value):
        """set article html."""
        value = '<div>' + self._replace_entities(value) + '</div>'
        html = gocept.lxml.objectify.fromstring(value)
        for node in self._html_getnodes():
            parent = node.getparent()
            parent.remove(node)
        body = self.xml['body']
        for node in html.iterchildren():
            if not node.countchildren() and not node.text:
                continue
            if node.text and not node.text.strip():
                continue

            if node.tag == 'h3':
                node.tag = 'intertitle'
            body.append(node)

    def _html_getnodes(self):
        for node in self.xml.body.iterchildren():
            if node.tag in ('p', 'intertitle'):
                yield node

    @property
    def paragraphs(self):
        return len(self.xml.body.findall('p'))

    @staticmethod
    def _replace_entities(value):
        # XXX is this efficient enough?
        for entity_name, codepoint in htmlentitydefs.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&'+entity_name+';', unichr(codepoint))
        return value


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def articleFactory(context):
    article = Article(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        context.properties)
    return article


@zope.interface.implementer(zeit.content.article.interfaces.IArticle)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def articleFromTemplate(context):
    source = StringIO.StringIO(
        zeit.cms.content.interfaces.IXMLSource(context))
    article = Article(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context))
    return article


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'article')
resourceFactory = zope.component.adapter(
    zeit.content.article.interfaces.IArticle)(resourceFactory)


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def updateTextLengthOnChange(object, event):
    length = zope.security.proxy.removeSecurityProxy(object.xml).body.xpath(
        'string-length()')
    try:
        object.textLength = int(length)
    except zope.security.interfaces.Unauthorized:
        # Ignore when we're not allowed to set it.
        pass
