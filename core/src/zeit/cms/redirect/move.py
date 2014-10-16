from zeit.cms.content.interfaces import WRITEABLE_LIVE
import grokcore.component as grok
import zeit.cms.redirect.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.relation.corehandlers
import zope.component
import zope.lifecycleevent.interfaces


class RenameInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.redirect.interfaces.IRenameInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.redirect.interfaces.IRenameInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('previous_uniqueIds',),
        writeable=WRITEABLE_LIVE, use_default=True)


class Dummy(object):

    uniqueId = None


@grok.subscribe(
    zeit.cms.repository.interfaces.IRepositoryContent,
    zope.lifecycleevent.interfaces.IObjectMovedEvent)
def store_redirect(context, event):
    if not all([event.oldParent, event.newParent,
                event.oldName, event.newName]):
        return
    lookup = zope.component.getUtility(zeit.cms.redirect.interfaces.ILookup)
    old_id = event.oldParent.uniqueId + event.oldName
    new_id = event.newParent.uniqueId + event.newName
    lookup.rename(old_id, new_id)
    zeit.cms.redirect.interfaces.IRenameInfo(
        context).previous_uniqueIds += (old_id,)
    # We need to update objects referencing the old name. But context already
    # has the new name, so we need to substitute a dummy with the old name.
    dummy = Dummy()
    dummy.uniqueId = old_id
    zeit.cms.relation.corehandlers.update_referencing_objects(dummy)
