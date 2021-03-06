from __future__ import absolute_import
import elasticsearch
import elasticsearch.connection
import elasticsearch.transport
import json
import pkg_resources
import requests.utils
import zeit.cms.interfaces
import zeit.retresco.interfaces
import zope.dottedname.resolve
import zope.interface


class Connection(elasticsearch.connection.RequestsHttpConnection):

    def __init__(self, *args, **kw):
        super(Connection, self).__init__(*args, **kw)
        self.session.headers['User-Agent'] = self._user_agent()

    def _user_agent(self):
        return requests.utils.default_user_agent(
            'zeit.retresco-%s/python-requests' % (
                pkg_resources.get_distribution('vivi.core').version))


def TransportWithConnection(connection_class):
    def factory(*args, **kw):
        kw['connection_class'] = connection_class
        return elasticsearch.transport.Transport(*args, **kw)
    return factory


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class Elasticsearch(object):
    """Search via Elasticsearch."""

    def __init__(self, url, index, connection_class=Connection):
        self.client = elasticsearch.Elasticsearch(
            [url], transport_class=TransportWithConnection(connection_class))
        self.index = index

    def search(
            self, query, sort_order='',
            start=0, rows=25, include_payload=False):
        """Search using `query` and sort by `sort_order`. Pagination is
        available through the `start` and `rows` parameter.

        The search results include the entire payload node (as specified by
        our schema), if the `include_playload` flag is set.

        To select specific fields, the `query` may include a `_source` node.
        Hint: A custom `_source` definition is mutually exclusive with the
        `include_payload` flag.
        """

        query = query.copy()
        if '_source' in query:
            if include_payload:
                raise ValueError(
                    'Cannot include payload with specified source: %s' %
                    (query['_source'],))
        else:
            query['_source'] = ['url', 'doc_type', 'doc_id']
            if include_payload:
                query['_source'].append('payload')

        __traceback_info__ = (self.index, query)
        response = self.client.search(
            index=self.index, body=json.dumps(query),
            sort=sort_order, from_=start, size=rows, doc_type='documents')
        result = zeit.cms.interfaces.Result(
            [x['_source'] for x in response['hits']['hits']])
        result.hits = response['hits']['total']
        return result

    def date_range(self, start, end):
        return date_range(start, end)


def date_range(start, end):
    result = {}
    if start is not None:
        result['gte'] = start.isoformat()
    if end is not None:
        result['lte'] = end.isoformat()
    return result


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
def from_product_config():
    """Get the utility configured with data from the product config."""
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    return Elasticsearch(
        config['elasticsearch-url'], config['elasticsearch-index'],
        zope.dottedname.resolve.resolve(
            config['elasticsearch-connection-class']))
