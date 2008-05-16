# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import cjson
import lxml.etree

import zope.component
import zope.interface
import zope.formlib.namedtemplate

import zope.app.form.browser.interfaces
import zope.app.form.browser.textwidgets
import zope.app.form.interfaces
import zope.app.pagetemplate

import zc.form.browser.combinationwidget

import zeit.cms.content.interfaces
import zeit.cms.content.sources


class XMLTreeWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def _toFieldValue(self, input):
        try:
            return self.context.fromUnicode(input)
        except zope.schema.ValidationError, e:
            raise zope.app.form.interfaces.ConversionError(e)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        else:
            # Etree very explicitly checks for the type and doesn't like a
            # proxied object
            value = zope.proxy.removeAllProxies(value)
            if value.getparent() is None:
                # When we're editing the whole tree we want to serialize the
                # root tree to get processing instructions.
                value = value.getroottree()
            return lxml.etree.tounicode(value, pretty_print=True).replace(
                '\n', '\r\n')


class XMLSnippetWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def _toFieldValue(self, input):
        as_unicode = super(XMLSnippetWidget, self)._toFieldValue(input)
        if as_unicode:
            return self.context.fromUnicode(as_unicode)
        return as_unicode


class CombinationWidget(
    zc.form.browser.combinationwidget.CombinationWidget):
    """Subclassed combination widget to change the template.

    NamedTemplate doesn't take the request into account so we cannot register a
    new template in our skin. This sucks.

    """

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'combinationwidget.pt')


class SubNavigationUpdater(object):

    navigation_source = zeit.cms.content.sources.NavigationSource()
    subnavigation_source = zeit.cms.content.sources.SubNavigationSource()

    def __init__(self, context, request):
        super(SubNavigationUpdater, self).__init__(context, request)
        self.master_terms = zope.component.getMultiAdapter(
            (self.navigation_source, request),
            zope.app.form.browser.interfaces.ITerms)

    def __call__(self, master_token):
        master_value = self.master_terms.getValue(master_token)

        class Fake(object):
            zope.interface.implements(
                zeit.cms.content.interfaces.ICommonMetadata)
            ressort = master_value

        source = self.subnavigation_source(Fake())
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.app.form.browser.interfaces.ITerms)
        result = []
        for value in source:
            term = terms.getTerm(value)
            result.append((term.title, term.token))
        return cjson.encode(sorted(result))
