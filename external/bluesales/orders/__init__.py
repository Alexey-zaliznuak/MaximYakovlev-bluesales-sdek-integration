from datetime import datetime, timedelta
from typing import List

from progress.bar import Bar as Bar

from external.bluesales.api_methods import OrdersMethods
from external.bluesales.exceptions import TooLargeBoarders
from external.bluesales.request_api import RequestApi

from .get_response import GetOrdersResponse
from .goods_positions_custom_fields import GoodsPositionsCustomFieldsService
from .order import Order
from .orders_custom_fields import OrdersCustomFieldsService
from .utils import OrdersUtils

MAX_COUNT_CUSTOMERS_PER_REQUEST = 500


class OrdersService:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api
        self.order_custom_fields = OrdersCustomFieldsService()
        self.goods_positions_custom_fields = GoodsPositionsCustomFieldsService()
        self.utils = OrdersUtils(self.order_custom_fields, self.goods_positions_custom_fields)

    def get(
            self,
            date_from: datetime = None,
            date_to: datetime = None,
            order_statuses: list = None,
            ids: List[int] = None,
            internal_numbers: List[int] = None,
            customer_id: int = None,
            count: int = 500,
            offset: int = 0
    ) -> 'GetOrdersResponse':
        if order_statuses is None:
            order_statuses = []
        if count > MAX_COUNT_CUSTOMERS_PER_REQUEST:
            raise TooLargeBoarders(
                f'Количество запрашиваемых клиентов за раз должно быть меньше {MAX_COUNT_CUSTOMERS_PER_REQUEST}'
            )
        out_statuses = []
        for status in order_statuses:
            if isinstance(status, int):
                out_statuses.append({'id': status})
            elif isinstance(status, str):
                out_statuses.append({'name': status})
            else:
                raise TypeError(f'Ожидалось int или str, получил {type(status)}')

        data = {
            'dateFrom': date_from.strftime('%Y-%m-%d') if date_from else None,
            'dateTill': (date_to + timedelta(days=1)).strftime(
                '%Y-%m-%d') if date_to else None,
            'orderStatuses': out_statuses,
            'customerId': customer_id,
            'ids': ids,
            'internalNumbers': internal_numbers,
            'pageSize': count,
            'startRowNumber': offset,
        }
        response = self.request_api.send(
            OrdersMethods.get,
            data=data
        )

        return GetOrdersResponse(response)

    def get_all(
            self,
            date_from: datetime = None,
            date_to: datetime = None,
            order_statuses: list = None,
            ids: List[int] = None,
            internal_numbers: List[int] = None,
            customer_id: int = None,
    ) -> List[Order]:

        items = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST
        offset = 0

        r = self.get(
            date_from, date_to, order_statuses,
            ids, internal_numbers, customer_id,
            count=1, offset=0
        )
        total_count = r.not_returned_count + r.count

        if total_count == 0:
            return []

        with Bar(f'Orders | {self.request_api.login}',
                 max=total_count, fill='█', empty_fill=' ') as bar:
            while len(items) < total_count:
                r = self.get(
                    date_from, date_to, order_statuses,
                    ids, internal_numbers, customer_id,
                    count, offset
                )
                items.extend(r.orders)
                offset += count
                bar.next(r.count)
        return items

    def set_many_statuses(
        self,
        data: list[tuple[str, str]]
    ):
        grouped_data = {}

        for order_id, status in data:
            if status not in grouped_data:
                grouped_data[status] = []
            grouped_data[status].append(str(order_id))

        for crm_status, ids in grouped_data.items():
            if not ids:
                continue

            print(f"Обновление {len(ids)} заказов до статуса '{crm_status}'.")

            data = {
                "ids": ids,
                "orderStatus": {
                    "id": crm_status
                },
            }

            try:
                response = self.request_api.send(
                    OrdersMethods.update_many,
                    data=data
                )

                if isinstance(response, str):
                    print(f"Результат обновления {len(ids)} заказов до статуса '{crm_status}': '{response}'")
                elif response.success:
                    print(f"Успешно обновлено {len(ids)} заказов до статуса '{crm_status}'.")
                else:
                    print(f"Ошибка при обновлении заказов до статуса '{crm_status}': {response.error}")

            except Exception as e:
                print(f"Исключение при обновлении заказов до статуса '{crm_status}': {e}")
