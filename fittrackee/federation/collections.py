from typing import Dict

from flask_sqlalchemy import BaseQuery, Pagination

from fittrackee.federation.constants import CONTEXT


class OrderedCollection:
    def __init__(self, url: str, base_query: BaseQuery) -> None:
        self._url = url
        self._base_query = base_query
        self._type = 'OrderedCollection'

    def serialize(self) -> Dict:
        return {
            '@context': CONTEXT,
            'id': self._url,
            'first': f'{self._url}?page=1',
            'totalItems': self._base_query.count(),
            'type': self._type,
        }


class OrderedCollectionPage:
    def __init__(self, url: str, pagination: Pagination) -> None:
        self._url = url
        self._pagination = pagination
        self._type = 'OrderedCollectionPage'

    def serialize(self) -> Dict:
        ordered_items = [
            user.actor.activitypub_id for user in self._pagination.items
        ]
        page = self._pagination.page
        collection_page_dict = {
            '@context': CONTEXT,
            'id': f'{self._url}?page={page}',
            'orderedItems': ordered_items,
            'partOf': self._url,
            'totalItems': self._pagination.total,
            'type': self._type,
        }
        if self._pagination.has_next and self._pagination.total > 0:
            collection_page_dict['next'] = f'{self._url}?page={page + 1}'
        if self._pagination.has_prev and self._pagination.total > 0:
            collection_page_dict['prev'] = f'{self._url}?page={page - 1}'
        return collection_page_dict
