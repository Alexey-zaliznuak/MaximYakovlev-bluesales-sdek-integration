# !/home/alexey/bluesales-cdek-transfering-integration/venv/bin/python

# /home/alexey/projects/MaximYakovlev-bluesales-sdek-integration/venv/bin/python /home/alexey/projects/MaximYakovlev-bluesales-sdek-integration/main.py
import json
import logging
import os
from datetime import datetime, timedelta
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
import random
from time import sleep
from typing import List

from external.bluesales import BlueSalesService
from external.bluesales.exceptions import BlueSalesError
from external.bluesales.orders import Order
from external.cdek import Client
from requests.exceptions import HTTPError
from settings import Settings

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(f"{Settings.BASE_FILES_PATH}log.log", maxBytes=64*1024, backupCount=3, encoding='utf-8')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

full_file_handler = RotatingFileHandler(f"{Settings.BASE_FILES_PATH}full_log.log", maxBytes=256*1024, backupCount=3, encoding='utf-8')
full_file_handler.setFormatter(formatter)
full_file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(full_file_handler)

stream_handler = StreamHandler()
stream_formatter = logging.Formatter("%(message)s")
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

BLUESALES = BlueSalesService(Settings.BLUESALES_LOGIN, Settings.BLUESALES_PASSWORD)
CDEK = Client(Settings.CDEK_CLIENT_ID, Settings.CDEK_CLIENT_SECRET)

def notify_that_orders_in_pvz(orders: List[Order]):
    if not orders:
        return

    logger.info("\n=== Рассылка уведомления о доставке в пунты выдачи / постаматы ===")

    for order in orders:
        order_contact_data = (
            f"Айди клиента в вк: {order.customer_vk_id}, "
            f"Айди группы переписки клиента в вк: {order.customer_vk_messages_group_id}, "
            f"https://bluesales.ru/app/Customers/OrderView.aspx?id={order.id}"
        )

        if not (order.customer_vk_id and order.customer_vk_messages_group_id):
            logger.info(f"У клиента не указаны данные в вк для уведомления. {order_contact_data}")
            continue

        vk = Settings.VK_CLIENTS_BY_GROUP_ID[order.customer_vk_messages_group_id]
        result = vk.messages.send(
            user_id=order.customer_vk_id,
            # message=Settings.text_for_postomat if is_postomat else Settings.text_for_pvz,
            message=Settings.text_for_pvz(),
            # random_id=int.from_bytes(os.urandom(8), byteorder="big")
            random_id=int(random.getrandbits(63))
        )
        logger.debug("Результат отправки: " + str(result))
        logger.info(f"Отправка уведомления что заказ в пвз/постомате. {order_contact_data}")

def process_delayed_orders(new_orders: List[Order]):
    updated_orders: list[Order] = []

    if not (10 < datetime.now().hour + 3 < 15):
        logger.info("\n=== Отложенные сообщения не рассматриваются из за времени ===")
        return

    logger.info("\n=== Загрузка данных о доставленных заказах ===")
    with open(Settings.BASE_FILES_PATH + "delievered_dates.json", "r", encoding="utf-8") as f:
        orders: list[dict] = json.load(f) # type: ignore

        for i, order in enumerate(orders):
            orders[i] = Order({**order["order"], "delivered_date": order["delivered_date"]}) # type: ignore
            # print(orders[i].delivered_date, orders[i].order, flush=True)

        for i in range(len(new_orders)):
            new_orders[i].delivered_date = datetime.now().isoformat()

        # orders.extend(new_orders)
        orders: list[Order] = orders

        for order in orders:
            if (datetime.fromisoformat(order.delivered_date) - datetime.now()).days > 4:
                status = CDEK.get_order_info(order.tracking_number)["entity"]["statuses"][0]["code"]
                if status not in ["POSTOMAT_RECEIVED", "DELIVERED",]:
                    order_contact_data = (
                        f"Айди клиента в вк: {order.customer_vk_id}, "
                        f"Айди группы переписки клиента в вк: {order.customer_vk_messages_group_id}, "
                        f"https://bluesales.ru/app/Customers/OrderView.aspx?id={order.id}"
                    )

                    if not (order.customer_vk_id and order.customer_vk_messages_group_id):
                        logger.info(f"У клиента не указаны данные в вк для уведомления. {order_contact_data}")
                        continue

                    vk = Settings.VK_CLIENTS_BY_GROUP_ID[order.customer_vk_messages_group_id]
                    result = vk.messages.send(
                        user_id=order.customer_vk_id,
                        message=Settings.text_for_dont_forget_expriration,
                        random_id=int.from_bytes(os.urandom(16), byteorder="big")
                    )
                    logger.debug("Результат отправки: " + str(result))
                    logger.info(f"Отправка уведомления что заказ ожидает уже 5 дней. {order_contact_data}")

                continue  # после 4 дней, независимо - находится ли в пункте или забрал, заказ в памяти нам больше не нужен
            updated_orders.append(order)

    with open(Settings.BASE_FILES_PATH + "delievered_dates.json", "w", encoding="utf-8") as f:
        json.dump([o.__dict__ for o in updated_orders], f, indent=4, ensure_ascii=False)
        logger.info("\n=== Уведомления с просьбой забрать заказ разосланы ===")

def get_crm_status_by_cdek(current_crm_status: str, cdek_status_name: str):
    return Settings.CDEK_TO_CRM_STATUS_ID.get(cdek_status_name, current_crm_status)

def main(*args, **kwargs):
    bluesales_orders = []

    for _ in range(3):
        try:
            bluesales_orders = BLUESALES.orders.get_all(date_from=datetime.today() - timedelta(days=60))
            break
        except BlueSalesError as e:
            print(e, "sleep 30 seconds...")
            sleep(30)

    print("Всего:", len(bluesales_orders), "сделок")

    # отсеиваем у кого нет статуса или номера трекера
    bluesales_orders = list(filter(
        lambda o:
            o.tracking_number
            and o.status_name
            and o.status_name not in ["Заказ выполнен",],
        bluesales_orders
        )
    )

    print("Активных", len(bluesales_orders), "сделок")

    update_orders = []

    orders_notify_that_order_in_pvz = []  # заказы, заказчикам которых нужно сделать уведу что из заказ в ПВЗ
    delayed_orders = []  # заказы, заказчикам которых нужно сделать уведу что прошло 5 дней

    for order in bluesales_orders:
        try:
            # if order.status_name in ["Разбор", "Правки заказа"]:
                # continue

            cdek_status = CDEK.get_order_info(order.tracking_number)["entity"]["statuses"][0]["code"]

            # logger.debug(" ".join([str(order.id), order.tracking_number, cdek_status, "crm status: ", order.status_name, " -> ", Settings.INVERTED_STATUSES[get_crm_status_by_cdek(order.status_name, cdek_status)]]))

            if (
                cdek_status != 'CREATED' and
                Settings.STATUSES[order.status_name] != get_crm_status_by_cdek(order.status_name, cdek_status)  # статус поменялся
            ):
                update_orders.append([order.id, get_crm_status_by_cdek(order.status_name, cdek_status)])  # для обновления времени

                if get_crm_status_by_cdek(order.status_name, cdek_status) == Settings.STATUSES["Заказ выполнен"]:
                    is_postomat = cdek_status == "POSTOMAT_POSTED"
                    orders_notify_that_order_in_pvz.append(order)
                    delayed_orders.append(order)

        except HTTPError as e:
            pass
            # logger.error(f"Ошибка, {order.tracking_number}")
            # {'requests': [{'type': 'GET', 'date_time': '2025-06-12T19:57:51+0000', 'state': 'INVALID', 'errors': [{'code': 'v2_order_not_found', 'additional_code': '0x7B234F39', 'message': 'Order not found by cdek_number 10118868207'}]}], 'related_entities': []}
            # logger.error(e.response.json())

    BLUESALES.orders.set_many_statuses(update_orders)

    notify_that_orders_in_pvz(orders_notify_that_order_in_pvz)
    process_delayed_orders(delayed_orders)

if __name__ == "__main__":
    logger.info(
        "=" * 10 + "  " + datetime.now().strftime("%d-%m-%Y %H:%M") + "  " + "=" * 10
    )
    try:
        main()
    except TimeoutError as e:
        logger.error(e)
    finally:
        logger.info("\n"*2)
