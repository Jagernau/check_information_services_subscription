# main.py
import datetime
import time
from collections import defaultdict

import schedule
import crud
from okdesk_handler import create_iss_okdesk
from my_logger import logger

def job():
    logger.info("Запуск задачи по расписанию.")
    try:
        now_time = datetime.datetime.now()
        logger.info(f"Текущая дата/время: {now_time}")

        # Получаем подписки, которые нужно оповестить сегодня
        subs_to_notify = crud.get_all_subs_from_time(now_time)
        if not subs_to_notify:
            logger.info("Нет подписок, требующих оповещения сегодня.")
            return "Нет подписок для оповещения"

        logger.info(f"Получено {len(subs_to_notify)} записей для оповещения.")

        # Группируем по клиенту (ok_desk_id)
        expiring_clients = defaultdict(lambda: {'company_name': '', 'objects': [], 'days_left': None})
        for sub in subs_to_notify:
            try:
                ca_name = sub[0]           # models.Contragents.ca_name
                sub_end = sub[1]           # subscription_end
                ok_desk_id = sub[2]        # ok_desk_id
                obj_name = sub[3]          # object_name
                stealth_type = sub[4]      # stealth_type
                days_left = sub[5]         # subs_day_send

                if not ok_desk_id:
                    logger.warning(f"Пропущен объект {obj_name}: нет ok_desk_id у клиента {ca_name}")
                    continue

                expiring_clients[ok_desk_id]['company_name'] = ca_name
                expiring_clients[ok_desk_id]['objects'].append({
                    'name': obj_name,
                    'type': stealth_type
                })
                expiring_clients[ok_desk_id]['days_left'] = days_left  # у всех объектов одного клиента одинаковое значение
            except (IndexError, TypeError, AttributeError) as e:
                logger.warning(f"Некорректная запись подписки, пропущена: {sub}. Ошибка: {e}")
                continue

        logger.info(f"Сгруппировано в {len(expiring_clients)} клиентов.")

        success_count = 0
        for ok_desk_id, data in expiring_clients.items():
            try:
                logger.info(f"Создаём заявку для клиента ID={ok_desk_id}, "
                            f"компания={data['company_name']}, объектов={len(data['objects'])}, "
                            f"дней до окончания={data['days_left']}")
                create_iss_okdesk(
                    client_okdesk_id=ok_desk_id,
                    company_name=data['company_name'],
                    objects_list=data['objects'],
                    days_left=data['days_left']
                )
                success_count += 1
                logger.info(f"Заявка для клиента {ok_desk_id} успешно создана.")
            except Exception as e:
                logger.error(f"Ошибка при создании заявки для клиента {ok_desk_id}: {e}")

        result = f"Обработано клиентов: {len(expiring_clients)}. Успешно создано заявок: {success_count}"
        logger.info(result)
        return result

    except Exception as e:
        logger.error("Непредвиденная ошибка в задаче job()")
        return f"Глобальная ошибка: {e}"

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Запуск планировщика. Задача запланирована ежедневно в 07:00.")
    schedule.every().day.at("07:00").do(job)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logger.error("Ошибка в основном цикле планировщика")
            time.sleep(60)
        time.sleep(30)
