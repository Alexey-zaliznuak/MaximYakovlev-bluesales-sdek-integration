# -*- coding: utf-8 -*-

class GoodsPositionsCustomFieldsService:
    def get_field_id_by_name(self, name: str) -> int:
        return {
            "Менеджеры": 1334,
            "Дата добавления": 1293,
        }[name]
