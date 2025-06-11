import pandas as pd

from external.bluesales.goods.goods import Goods


class GoodsUtils:
    def transform_to_dataframe(
        self,
        goods_list: list[Goods],
    ):
        rows = []

        for goods in goods_list:
            goods = goods.payload

            raw = {
                'id': goods.get("id"),
                'marking': goods.get("marking", None),
                'price': goods.get("price", None),
                'cost': goods.get("cost", None),
                'is_archived': goods.get("isArchived", None),
                'goods_type.id': goods.get("goodsType", {}).get("id", None),
                'goods_category.id': goods.get("goodsCategory", {}).get("id", None),
            }

            rows.append(raw)

        df = pd.DataFrame(rows)
        return df
