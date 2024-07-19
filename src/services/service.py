from typing import Optional, Type, TypeAlias

from db.cache import Cache
from models.model import Film, Genre, Person
from services.search.base import AbstractSearchService

CACHE_EXPIRE_IN_SECONDS = 60 * 5


ServiceItem: TypeAlias = Film | Genre | Person


class Service:
    def __init__(self, cache: Cache, search_service: AbstractSearchService, entity_name: str, model: Type[ServiceItem]):
        self.cache = cache
        self.search_service = search_service
        self.model = model
        self.entity_name = entity_name

    async def get_by_id(self, item_id: str) -> Optional[ServiceItem]:
        item = await self._get_from_cache(item_id)
        if not item:
            if item_dict := await self.search_service.get_by_id(item_id):
                item = self.model(**item_dict)
                await self._put_to_cache(item)
        return item

    async def _get_from_cache(self, item_id: str) -> Optional[ServiceItem]:
        data = await self.cache.get(f"{self.entity_name}_{item_id}")
        if not data:
            return None
        return self.model.model_validate_json(data)

    async def _put_to_cache(self, item: ServiceItem):
        await self.cache.put(f"{self.entity_name}_{item.id}", item.model_dump_json(), CACHE_EXPIRE_IN_SECONDS)

    async def get_by_text_field(self, search_field: str, search_text: str) -> Optional[ServiceItem]:
        items = await self.search_service.text_search(search_fields=[search_field], search_query=search_text)
        if items := await self.search_service.text_search(search_fields=[search_field], search_query=search_text):
            return self.model.model_validate(items[0])
