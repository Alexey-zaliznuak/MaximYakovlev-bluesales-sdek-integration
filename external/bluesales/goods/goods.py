class Goods:
    def __init__(self, payload: dict):
        self.id: int = payload.get('id')
        self.marking: int = payload.get('marking')
        self.price = payload.get("price", None)
        self.cost = payload.get("cost", None)
        self.is_archived = payload.get("isArchived", False)
        self.goods_type_id = payload.get("goodsType", {}).get("id", None)
        self.goods_category_id = payload.get("goodsCategory", {}).get("id", None)

        self.payload = payload
