import pandas as pd

from external.bluesales.utils import get_property_safely

from .goods_positions_custom_fields import GoodsPositionsCustomFieldsService
from .order import Order
from .orders_custom_fields import OrdersCustomFieldsService


class MergeCustomOrdersFieldSettings:
    def __init__(self, field_id: int, column_name: str):
        self.field_id = field_id
        self.column_name = column_name

class MergeCustomGoodsPositionsFieldSettings:
    def __init__(self, field_id: int, column_name: str, include_value_as_text: bool = False):
        self.field_id = field_id
        self.column_name = column_name
        self.include_value_as_text = include_value_as_text



class OrdersUtils:
    def __init__(
        self,
        custom_order_fields_service: OrdersCustomFieldsService,
        custom_goods_positions_fields_service: GoodsPositionsCustomFieldsService,
    ):
        self.custom_order_fields_service = custom_order_fields_service
        self.custom_goods_positions_fields_service = custom_goods_positions_fields_service

    def transform_to_dataframe(
        self,
        orders: list[Order],
        *,
        fields_only_in_first_goods: list[str] = [],
        merge_custom_order_fields: list[MergeCustomOrdersFieldSettings] = None,
        merge_custom_goods_positions_fields: list[MergeCustomGoodsPositionsFieldSettings] = None,
        goods_to_merge: pd.DataFrame = None
    ):
        rows = []

        for order in orders:
            order = order.payload

            # Создаем пустого менеджера если его нет
            order["manager"] = {} if order["manager"] is None else order["manager"]

            # Разбираем базовую информацию о заказе
            base_info = {
                "id": order["id"],
                "customer.id": order["customer"]["id"],
                "customer.full_name": order["customer"]["fullName"],
                "customer.birthday": order["customer"]["birthday"],
                "customer.sex": order["customer"]["sex"],
                "customer.city": order["customer"]["city"]["name"] if order["customer"].get("city") else None,
                "customer.country": order["customer"]["country"]["name"] if order["customer"].get("country") else None,
                "customer.first_contact_date": get_property_safely(order, "customer.firstContactDate", None),
                "tags": ";".join([tag["name"] for tag in order["customer"].get("tags", [])]),
                "manager.id": order["manager"].get("id", None),
                "manager.full_name": order["manager"].get("fullName", None),
                "manager.email": order["manager"].get("email", None),
                "manager.phone": order["manager"].get("phone", None),
                "date": order["date"],
                "orders_status": order["orderStatus"]["name"],
                "total_sum_minus_discount": order["totalSumWithoutDiscount"],
                "discount": order["discount"],
                "total_sum_minus_discount": order["totalSumMinusDiscount"],
                "delivery_cost": order["deliveryCost"],
                "delivery_price": order["deliveryPrice"],
                "total_sum_with_delivery": order["totalSumWithDelivery"],
                "prepay": order["prepay"],
            }

            base_info = self.merge_custom_order_fields(base_info, order, merge_custom_order_fields)

            # Если товаров нет добавляем 1 строку без данных о товаре
            if len(order["goodsPositions"]) == 0:
                goods_info = {
                    "goods_positions.number": 1,
                    "goods.id": "",
                    "goods.marking": "",
                    "goods.name": "",
                    "goods.weight": "",
                    "goods.size": "",
                    "goods.price": "",
                    "goods.quantity": ""
                }
                row = {**base_info, **goods_info}
                rows.append(row)

            else:
                # Разбираем каждую позицию товара в заказе, для каждой позиции - своя строка
                for goods_number, goods_position in enumerate(order["goodsPositions"], start=1):
                    goods_info = {
                        "goods_positions.number": goods_number,
                        "goods.id": goods_position["goods"]["id"],
                        "goods.marking": goods_position["goods"]["marking"],
                        "goods.name": goods_position["goods"]["name"],
                        "goods.weight": goods_position["goods"].get("weight"),
                        "goods.size": goods_position.get("size"),
                        "goods.price": goods_position["price"],
                        "goods.quantity": goods_position["quantity"],
                    }

                    self.merge_custom_goods_positions_fields(goods_info, goods_position, merge_custom_goods_positions_fields)

                    # Объединяем общую информацию заказа и конкретно текущей позицией
                    row = {**base_info, **goods_info}

                    # удаление полей которые должны быть только в первом товаре
                    if goods_number > 1 and fields_only_in_first_goods:
                        row = {k: v for k, v in row.items() if k not in fields_only_in_first_goods}

                    rows.append(row)


        df = pd.DataFrame(rows)

        if goods_to_merge is not None:
            df = self.merge_with_goods(df, goods_to_merge)
        return df

    def merge_with_goods(self, orders_df: pd.DataFrame, goods_to_merge_df: pd.DataFrame) -> pd.DataFrame:
        """
        Соединяет DataFrame orders с DataFrame goods_to_merge на основе goods.id,
        добавляя колонки из goods_to_merge с префиксом 'goods.'.

        :param orders_df: DataFrame заказов, содержащий колонку 'goods.id'
        :param goods_to_merge_df: DataFrame товаров, содержащий колонку 'id' и другие атрибуты
        :return: Объединённый DataFrame
        """
        # Проверяем, что 'goods.id' существует в orders_df
        if 'goods.id' not in orders_df.columns:
            raise ValueError("В DataFrame orders отсутствует колонка 'goods.id'")

        # Проверяем, что 'id' существует в goods_to_merge_df
        if 'id' not in goods_to_merge_df.columns:
            raise ValueError("В DataFrame goods_to_merge отсутствует колонка 'id'")

        # Убедимся, что 'id' в goods_to_merge_df уникальны
        if goods_to_merge_df['id'].duplicated().any():
            raise ValueError("Колонка 'id' в goods_to_merge содержит дубликаты. Убедитесь, что она уникальна.")

        # Переименовываем колонки в goods_to_merge, добавляя префикс 'goods.' за исключением 'id'
        goods_renamed = goods_to_merge_df.rename(
            columns=lambda x: f'goods.{x}' if x != 'id' else 'goods.id'
        )

        # Выполняем соединение на основе 'goods.id'
        merged_df = orders_df.merge(
            goods_renamed,
            on='goods.id',
            how='left',
            suffixes=('', '_goods')  # На случай, если есть колонки с одинаковыми именами
        )

        return merged_df

    def merge_custom_order_fields(self, obj: dict, order_payload: dict, fields: list[MergeCustomOrdersFieldSettings]):
        parsed_fields = self.parse_order_custom_fields(order_payload)

        for field in fields:
            obj[field.column_name] = parsed_fields.get(field.field_id, None)

        return obj

    def parse_order_custom_fields(self, order_payload: dict) -> dict[int]:
        fields = {}

        for field in order_payload.get("customFields", []):
            fields[field["fieldId"]] = field["value"]

        return fields

    def merge_custom_goods_positions_fields(self, obj: dict, goods_positions_payload: dict, fields: list[MergeCustomGoodsPositionsFieldSettings]):
        parsed_fields = self.parse_goods_positions_custom_fields(goods_positions_payload, fields)

        for field in fields:
            obj[field.column_name] = parsed_fields.get(field.field_id, None)

        return obj

    def parse_goods_positions_custom_fields(self, data: dict, fields_settings: list[MergeCustomGoodsPositionsFieldSettings]) -> dict:
        fields = {}

        fields_settings = {
            f.field_id: {
                "include_value_as_text": f.include_value_as_text
            } for f in fields_settings
        }


        for field in data.get("customFields", []):
            field_settings = fields_settings.get(field["fieldId"], None)

            if field_settings is None:
                continue

            fields[field["fieldId"]] = field["valueAsText" if field_settings["include_value_as_text"] else "value"]

        return fields
