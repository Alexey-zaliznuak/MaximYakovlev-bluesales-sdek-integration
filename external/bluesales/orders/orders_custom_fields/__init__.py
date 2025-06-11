# -*- coding: utf-8 -*-
from external.bluesales.request_api import RequestApi


class OrdersCustomFieldsService:
    def get_field_id_by_name(self, name: str) -> int:
        return {
            "На ведение": 5853,
            "Дата 2 предоплаты": 4880,
            "Дата отправки": 5283,
            "Дата доставки": 5345,
            "Дата завершения": 4827,
            "Дата слета": 5488,
            "Дата возврата": 5841,
            "Дата разбора": 5805,
        }[name]
