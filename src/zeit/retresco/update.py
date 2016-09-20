import argparse
import gocept.async
import gocept.runner
import grokcore.component as grok
import logging
import zeit.cms.async
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.lifecycleevent


log = logging.getLogger(__name__)


@grok.subscribe(zope.lifecycleevent.IObjectAddedEvent)
def index_after_add(event):
    # We don't use the "extended" (object, event) method, as we are not
    # interested in the events which are dispatched to sublocations.
    context = event.object
    if not zeit.cms.interfaces.ICMSContent.providedBy(context):
        return
    if zeit.cms.repository.interfaces.IRepository.providedBy(context):
        return
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.newParent):
        return
    log.info('AfterAdd: Creating async index job for %s (async=%s)' % (
        context.uniqueId, gocept.async.is_async()))
    index_async(context.uniqueId, enrich=True)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def index_after_checkin(context, event):
    index_async(context.uniqueId, enrich=True)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectRemovedEvent)
def unindex_on_remove(context, event):
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.oldParent):
        return
    unindex_async(zeit.cms.content.interfaces.IUUID(context).id)


@zeit.cms.async.function(queue='search')
def index_async(uniqueId, enrich=False):
    context = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if context is None:
        log.warning('Could not index %s because it does not exist any longer.',
                    uniqueId)
    else:
        index(context, enrich)


def index(content, enrich=False):
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    stack = [content]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        log.info('Updating: %s', content.uniqueId)
        try:
            body = None
            if enrich:
                response = conn.enrich(content)
                body = response.get('body')
            if body:
                conn.index(content, body)
            else:
                conn.index(content)
        except zeit.retresco.interfaces.TMSError:
            log.warning('Error indexing %s', content.uniqueId, exc_info=True)
            continue


@zeit.cms.async.function(queue='search')
def unindex_async(uuid):
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    conn.delete_id(uuid)


@zeit.cms.celery.task()
def index_parallel(unique_id, enrich=False):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    # Performance optimization: Resolve content directly via Connector instead
    # of traversing every folder.
    content = repository.getUncontainedContent(
        zeit.connector.connector.CannonicalId(unique_id))

    if zeit.cms.repository.interfaces.ICollection.providedBy(content):
        children = content.values()
    else:
        children = [content]

    for item in children:
        log.debug('Looking at %s', item.uniqueId)
        if (zeit.content.image.interfaces.IImageGroup.providedBy(item) or
                zeit.content.image.interfaces.IImage.providedBy(item)):
            log.debug(
                'Skip indexing %s, it is an image/group', item.uniqueId)
            continue
        if zeit.cms.repository.interfaces.ICollection.providedBy(item):
            index_parallel.delay(item.uniqueId, enrich)
        else:
            index(item, enrich)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.retresco', 'index-principal'))
def reindex():
    parser = argparse.ArgumentParser(description='Reindex folder in TMS')
    parser.add_argument(
        'ids', type=unicode, nargs='+', help='uniqueIds to reindex')
    parser.add_argument(
        '--parallel', action='store_true',
        help='process via job queue instead of directly')
    parser.add_argument(
        '--enrich', action='store_true',
        help='Perform TMS analyze/enrich prior to indexing')

    args = parser.parse_args()
    for id in args.ids:
        if args.parallel:
            index_parallel.delay(id, args.enrich)
        else:
            index(zeit.cms.interfaces.ICMSContent(id))