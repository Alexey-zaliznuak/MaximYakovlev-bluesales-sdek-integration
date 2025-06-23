from external.bluesales.utils import get_property_safely
from settings import Settings

class Order:
    def __init__(self, order: dict = {}):
        self.order = order
        self.id: int = order.get('id')
        self.status_name = order.get("orderStatus", {}).get("name", None)
        self.status_id = order.get("orderStatus", {}).get("id", None)

        self.customer = order.get("customer", {})
        self.customer_id = order.get("customer", {}).get("id", None)
        self.customer_vk = self.customer.get("vk", {}) if self.customer else None
        self.customer_vk_id = self.customer_vk.get("id", {}) if self.customer_vk else None
        self.customer_vk_messages_group_id = self.customer_vk.get("messagesGroupId", {}) if self.customer_vk else None

        self.delivered_date = order.get("delivered_date", "")

        self.tracking_number = None
        for custom_field in order.get('customFields', []):
            if custom_field.get('fieldId', None) == Settings.TRACKING_NUMBER_FIELD_ID:  # айди кастомного поля - айди для сдека
                self.tracking_number = custom_field.get("value", None)
                break

        # for k, v in kwargs.items():
        #     self.__setattr__(k, v)
