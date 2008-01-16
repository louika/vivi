# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.form.browser.textwidgets

import gocept.form.grouped
import zc.resourcelibrary

import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _



class ShowLimitInputWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        zc.resourcelibrary.need('zeit.cms.content.validation')
        max_length = self.context.max_length
        result = [
            '<div class="show-input-limit" maxlength="%s"></div>' % max_length,
        super(ShowLimitInputWidget, self).__call__(),
            ('<script language="javascript">new zeit.cms.InputValidation('
             '"%s");</script>') % self.name]

        return ''.join(result)


class CommonMetadataFormBase(object):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Navigation"),
            ('__name__', 'keywords', 'serie'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Head"),
            ('year', 'volume', 'page', 'ressort'),
            css_class='widgets-float column-left'),
        gocept.form.grouped.RemainingFields(
            _("Texts"),
            css_class='wide-widgets column-left'),
        gocept.form.grouped.Fields(
            _("misc."),
            ('authors', 'related', 'images', 'copyrights', 'pageBreak',
             'automaticTeaserSyndication'),
            css_class= 'column-right'),
        )

    for_display = False

    def __init__(self, context, request):
        super(CommonMetadataFormBase, self).__init__(context, request)

        if not self.for_display:
            # Change the widgets of the teaser fields
            for field in ('teaserText',
                          'shortTeaserTitle', 'shortTeaserText'):
                self.form_fields[field].custom_widget = ShowLimitInputWidget

    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.cms.content.teaser')
        return super(CommonMetadataFormBase, self).template


class CommonMetadataAddForm(CommonMetadataFormBase,
                            zeit.cms.browser.form.AddForm):
    """Add form which contains the common metadata."""


class CommonMetadataEditForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.EditForm):
    """Edit form which contains the common metadata."""


class CommonMetadataDisplayForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.DisplayForm):
    """Display form which contains the common metadata."""

    for_display = True  # omit custom widget w/ js-validation
