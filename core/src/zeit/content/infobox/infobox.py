from zeit.cms.i18n import MessageFactory as _
import copy
import lxml.objectify
import rwproperty
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.infobox.interfaces
import zope.interface


class Infobox(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.infobox.interfaces.IInfobox,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = (
        u'<container layout="artbox" label="info" '
        u'xmlns:py="http://codespeak.net/lxml/objectify/pytype" '
        u'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />')

    supertitle = zeit.cms.content.property.ObjectPathProperty('.supertitle')

    @rwproperty.getproperty
    def contents(self):
        result = []
        for node in self.xml.findall('block'):
            text_node = node.find('text')
            if text_node is None:
                text_node = lxml.objectify.E.text()
            elif text_node.text:
                # There is text which is not wrapped into a node. Wrap it.
                text_node = lxml.objectify.E.text(
                    lxml.objectify.E.p(text_node.text,
                                       *text_node.getchildren()))
            text = self.html_converter.to_html(text_node)
            result.append((unicode(node['title']),
                           text))
        return tuple(result)

    @rwproperty.setproperty
    def contents(self, value):
        for node in self.xml.findall('block'):
            self.xml.remove(node)
        for title, text in value:
            text_node = lxml.objectify.E.text()
            html = self.html_converter.from_html(text_node, text)

            self.xml.append(lxml.objectify.E.block(
                lxml.objectify.E.title(title),
                text_node))
        self._p_changed = True

    @property
    def html_converter(self):
        return zeit.wysiwyg.interfaces.IHTMLConverter(self)


class InfoboxType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Infobox
    interface = zeit.content.infobox.interfaces.IInfobox
    type = 'infobox'
    title = _('Infobox')
