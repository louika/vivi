# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import gocept.form.grouped

import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.workflow.interfaces


class WorkflowForm(zeit.cms.browser.form.EditForm):

    title = _("Workflow")

    field_groups = (
        gocept.form.grouped.Fields(
            _("Status"),
            ('last_modified_by', 'date_last_modified',
             'published', 'date_first_released',
             'edited', 'corrected', 'refined', 'images_added'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("Einstellung"), css_class='column-right'),
    )

    form_fields = zope.formlib.form.Fields(
        zeit.workflow.interfaces.IWorkflow)

    @zope.formlib.form.action(_('Save state'))
    def handle_save_state(self, action, data):
        self.applyChanges(data)

    @zope.formlib.form.action(_('... and publish'))
    def handle_publish(self, action, data):
        self.applyChanges(data)
        publish = zeit.cms.workflow.interfaces.IPublish(self.context)
        mapping = dict(
            name=self.context.__name__,
            id=self.context.uniqueId)
        if publish.can_publish():
            publish.publish()
            self.send_message(_('scheduled-for-publishing',
                                mapping=mapping))
        else:
            self.send_message(_('publish-preconditions-not-met',
                                mapping=mapping),
                              type='error')
