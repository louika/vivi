# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import transaction
import urllib
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.formlib.form
import zope.i18n


class EditContentsMenuItem(zeit.cms.browser.menu.ContextViewsMenu):
    """The Workflow menu item which is active when no other item is active."""

    sort = -1
    viewURL = "@@edit.html"
    activeCSS = 'edit_contents selected'
    inActiveCSS = 'edit_contents'

    @property
    def title(self):
        """Changes wheter item is checkout or checked in"""
        checkout = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        if checkout.canCheckout:
            return _("View")
        return _("Edit contents")

    @property
    def selected(self):
        """We are selected when no other item is selected."""
        return self.request.getURL().endswith('@@edit.html')
