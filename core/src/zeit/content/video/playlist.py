from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import pkg_resources
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.content.video.interfaces
import zope.interface


@zope.interface.implementer(
    zeit.content.video.interfaces.IPlaylist,
    zeit.cms.interfaces.IAsset)
class Playlist(zeit.cms.content.metadata.CommonMetadata):

    default_template = pkg_resources.resource_string(
        __name__, 'playlist-template.xml').decode('utf-8')

    videos = zeit.cms.content.reference.MultiResource(
        '.body.videos.video', 'related')

    id_prefix = 'pls'


class PlaylistType(zeit.cms.type.XMLContentTypeDeclaration):

    title = _('Playlist')
    interface = zeit.content.video.interfaces.IPlaylist
    addform = zeit.cms.type.SKIP_ADD
    factory = Playlist
    type = 'playlist'


@grok.adapter(zeit.content.video.interfaces.IPlaylist, name='playlist')
@grok.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def references(context):
    if context.videos:
        return context.videos
    return []
