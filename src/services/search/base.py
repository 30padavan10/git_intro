from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from utils.params import CommonQueryParams


@dataclass
class NestedObjectQuery:
    """
    Вспомогательный класс для настройки поиска по вложенным объектам (связанным таблицам)
    """

    name: str
    filter_field: str
    term_value: str


class AbstractSearchService(ABC):
    """Абстрактный базовый класс для осуществления поиска"""

    @abstractmethod
    async def get_by_id(self, id: str) -> dict | None:
        """Метод для поиска одного элемента по id"""
        pass

    @abstractmethod
    async def get_list(
        self,
        params: CommonQueryParams | None = None,
        nested_objects: list[NestedObjectQuery] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Метод для получения списка элементов, поддерживат пагинацию и сортировку,
        а так же фильтрацию по вложенным объектам/связанным таблицам
        """
        pass

    @abstractmethod
    async def text_search(
        self,
        search_query: str | None,
        search_fields: list[str],
        params: CommonQueryParams | None = None,
    ) -> list[dict]:
        """
        Метод для полнотекстового поиска, ожидает поисковой запрос и список полей
        по которым будет происходить поиск, поддерживат пагинацию и сортировку
        """
        pass
