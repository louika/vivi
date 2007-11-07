# Copyright (c) 2006-2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interfaces for CMS skin"""

import zope.interface.common.mapping
import zope.publisher.interfaces.browser
import zope.viewlet.interfaces
import zope.interface
import zope.schema


class ICMSLayer(zope.publisher.interfaces.browser.IBrowserRequest):
    """Master Layer for CMS skin"""


class ICMSTestingSkin(ICMSLayer,
                      zope.publisher.interfaces.browser.IBrowserRequest,
                      zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """Layer/Skin which is only used in tests."""


class ICMSSkin(ICMSLayer,
               zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """CMS skin"""


class ISidebar(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the sidebar"""


class IListRepresentation(zope.interface.Interface):
    """List representation of content objects"""

    __name__ = zope.interface.Attribute("File name")
    uniqueId = zope.interface.Attribute("Unique ID in repository.")
    url = zope.schema.URI(title=u"URL to the object in the CMs.")

    title = zope.interface.Attribute("Content title")
    author = zope.interface.Attribute("Author")
    ressort = zope.interface.Attribute("Ressort")
    searchableText = zope.interface.Attribute("Index used to search the list")
    page = zope.schema.Int(title=u"Page in paper")
    volume = zope.schema.Int(title=u"Volume")
    year = zope.schema.Int(title=u"Year")

    url = zope.schema.URI(title=u"URL to View")

    workflowState = zope.interface.Attribute("Workflow State")

    modifiedBy = zope.interface.Attribute("Datetime of last modification")

    def modifiedOn(format=None):
        """Date of last modification.

        format: strftime format string,
        if format=None the formatstring is computed by using the server LOCALE

        """

    def createdOn(format=None):
        """Returns creation date as string.

        format: strftime format string,
        if format=None the formatstring is computed by using the server LOCALE

        """


class IImageRepresentation(zope.interface.Interface):
    """Image representation of content objects."""

    title = zope.interface.Attribute("Content title")
    thumbnailUrl = zope.interface.Attribute("Thumbnail url used for Preview")


class ITreeState(zope.interface.common.mapping.IMapping):
    """Saves the tree state for various trees."""


class ITree(zope.interface.Interface):
    """Tree rendering."""

    root = zope.interface.Attribute("The root of the tree.")

    def expandNode(self, id):
        """Expand the node identified by id."""

    def collapseNode(self, id):
        """Collapse the node identified by id."""


class IPanelState(zope.interface.Interface):
    """Remembers the state of panel folding.

    Calling foldPandel(...) results in the panel to be folded uppon the next
    request. Actual inline folding of a panel in the browser needs to be done
    with java script directly in the browser.

    """

    def folded(panel):
        """Return if `panel` is folded."""

    def foldPanel(panel):
        """Fold `pandel`."""

    def unfoldPanel(panel):
        """Unfold `pandel`."""


class ICMSUserPreferences(zope.interface.Interface):

    sidebarFolded = zope.schema.Bool(
        title=u"Sidebar folded?",
        default=False)
