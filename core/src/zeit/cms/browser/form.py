# Copyright (c) 2006-2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.formlib.interfaces

import zope.app.container.interfaces

import gocept.form.grouped

import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _


REMAINING_FIELDS = object()


def apply_changes_with_setattr(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = False

    for form_field in form_fields:
        field = form_field.field

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if newvalue is form_field:
            continue

        # Adapt context, if necessary
        interface = form_field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        if field.get(adapter) != newvalue:
            changed = True
            setattr(adapter, name, newvalue)

    return changed


metadataFieldGroups = (
    gocept.form.grouped.Fields(
        _("Navigation"),
        ('navigation', 'keywords', 'serie'),
        css_class='column-right'),
    gocept.form.grouped.Fields(
        _("Kopf"),
        ('year', 'volume', 'page', 'ressort'),
        css_class='widgets-float column-left'),
    gocept.form.grouped.Fields(
        _("Optionen"),
        ('dailyNewsletter', 'boxMostRead', 'commentsAllowed', 'banner'),
        css_class='widgets-float column-left'),
    gocept.form.grouped.RemainingFields(
        _("Texte"),
        css_class='wide-widgets column-left'),
    gocept.form.grouped.Fields(
        _("sonstiges"),
        ('authors', 'copyrights', 'pageBreak', 'automaticTeaserSyndication',
         'images'),
        css_class= 'column-right'),
    )

class FormBase(object):

    widget_groups = ()

    def applyChanges(self, object, data):
        return zope.formlib.form.applyChanges(
            object, self.form_fields, data, self.adapters)

    def setUpWidgets(self, ignore_request=False):
        if self.widget_groups:
            self._convert_to_fieldgroups()
        super(FormBase, self).setUpWidgets(ignore_request)

    def render(self):
        if self.status and not self.errors:
            # rendered w/o error
            next_url = self.nextURL()
            if next_url is not None:
                #self.send_message(self.status)  # XXX
                return self.request.response.redirect(next_url)
        return super(FormBase, self).render()

    def _convert_to_fieldgroups(self):
        """Convert old widget_group to gocept.form's field_groups.

        This is there so we don't need to manualle rewrite all the forms. Once
        all forms have been changed this code can be removed of course.

        """
        field_groups = []

        for title, field_names, css_class in self.widget_groups:
            if field_names is REMAINING_FIELDS:
                group = gocept.form.grouped.RemainingFields(
                    title, css_class)
            else:
                group = gocept.form.grouped.Fields(
                    title, field_names, css_class)
            field_groups.append(group)
        self.field_groups = field_groups


class AddForm(FormBase, gocept.form.grouped.AddForm):
    """Add form."""

    factory = None
    next_view = None
    checkout = True

    _checked_out = False

    def applyChanges(self, object, data):
        return apply_changes_with_setattr(
            object, self.form_fields, data, self.adapters)

    def create(self, data):
        if self.factory is None:
            raise ValueError("No factory specified.")
        new_object = self.factory()
        self.applyChanges(new_object, data)
        return new_object

    def add(self, object):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        name = chooser.chooseName(self.suggestName(object), object)
        self.context[name] = object
        object = self.context[name]

        # Check the document out right away (if possible).
        if self.checkout:
            manager = zeit.cms.checkout.interfaces.ICheckoutManager(
                self.context[name], None)
            if manager is not None and manager.canCheckout:
                object = manager.checkout()
                self._checked_out = True

        self._created_object = object
        self._finished_add = True

    def suggestName(self, object):
        return object.__name__

    def nextURL(self):
        if self.next_view:
            view = self.next_view
        elif self._checked_out:
            view = 'edit.html'
        else:
            view = 'view.html'
        url = zope.component.getMultiAdapter(
            (self._created_object, self.request), name='absolute_url')()
        return '%s/@@%s' % (url, view)

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            if 'form.actions.add' not in self.request:
                form = self.request.form
                form['form.year'] = str(datetime.datetime.now().year)
                volume = str(int(  # Strip leading 0
                    datetime.datetime.now().strftime('%W')))
                if volume == '0':
                    # I'm not sure that's right.
                    volume = '1'
                form['form.volume'] = volume
        super(AddForm, self).setUpWidgets(ignore_request)


class EditForm(FormBase, gocept.form.grouped.EditForm):
    """Edit form."""

    title = _("Edit")
    redirect_to_parent_after_edit = False
    redirect_to_view = None

    def nextURL(self):
        if (not self.redirect_to_parent_after_edit
            and not self.redirect_to_view):
            return None

        new_context = self.context
        if self.redirect_to_parent_after_edit:
            new_context = new_context.__parent__

        view = ''
        if self.redirect_to_view:
            view = '/@@%s' % self.redirect_to_view

        return '%s%s' % (
            zope.component.getMultiAdapter(
                (new_context, self.request), name='absolute_url')(),
            view)

class DisplayForm(FormBase, gocept.form.grouped.DisplayForm):
    """Display form."""

    title = _("View")
