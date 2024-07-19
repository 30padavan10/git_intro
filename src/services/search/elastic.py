from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

from services.search.base import AbstractSearchService, NestedObjectQuery
from utils.params import CommonQueryParams


class ElasticSearchService(AbstractSearchService):
    """Сервис поиска в Elasticsearch"""

    def __init__(self, elastic: AsyncElasticsearch, index: str):
        self.elastic = elastic
        self.index = index

    async def get_by_id(self, id: str) -> dict | None:
        """Поиска одного элемента по id"""
        try:
            doc = await self.elastic.get(index=self.index, id=id)
        except NotFoundError:
            return None
        return doc["_source"]

    async def get_list(
        self,
        params: CommonQueryParams | None = None,
        nested_objects: list[NestedObjectQuery] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Получение списка элементов, поддерживат пагинацию и сортировку,
        а так же фильтрацию по вложенным объектам/связанным таблицам
        """
        return await self._search(params, nested_objects)

    async def text_search(
        self,
        search_query: str | None,
        search_fields: list[str],
        params: CommonQueryParams | None = None,
    ) -> list[dict[str, Any]]:
        """
        Полнотекстового поиска, ожидает поисковой запрос и список полей
        по которым будет происходить поиск, поддерживат пагинацию и сортировку
        """
        if not search_query:
            query = None
        elif len(search_fields) == 1:
            query = {"match": {search_fields[0]: {"query": search_query, "fuzziness": "auto"}}}
        else:
            query = {"multi_match": {"query": search_query, "fields": search_fields}}
        return await self._search(
            params=params,
            search_query=query,
        )

    async def _search(
        self,
        params: CommonQueryParams | None = None,
        nested_objects: list[NestedObjectQuery] | None = None,
        search_query: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Общий метод поиска по elasticsearch, реализует пагинацию,
        сортировку и поиск по вложенным объектам/nested fields
        """
        if not params:
            params = CommonQueryParams()
        from_ = 0 if params.page_number == 1 else params.page_size * params.page_number - params.page_size

        sort = [{sort_field[1:]: "desc"} if sort_field[0] == "-" else {sort_field: "asc"} for sort_field in params.sort]
        sort.append({"_score": "desc"})

        query = {"bool": {"must": [], "should": []}}

        if search_query:
            query["bool"]["must"].append(search_query)

        if not nested_objects:
            nested_objects = []

        for nested_object in nested_objects:
            query["bool"]["should"].append(
                {
                    "nested": {
                        "path": nested_object.name,
                        "query": {
                            "bool": {
                                "filter": {
                                    "term": {
                                        f"{nested_object.name}.{nested_object.filter_field}": nested_object.term_value
                                    }
                                }
                            }
                        },
                    }
                }
            )

        response = await self.elastic.search(
            index=self.index, size=params.page_size, from_=from_, query=query, sort=sort
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
