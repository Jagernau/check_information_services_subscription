import datetime
import time
from collections import defaultdict

import schedule

import crud
from okdesk_handler import create_iss_okdesk
from my_logger import logger

# ---------- Основная задача ----------
def job():
    """
    Проверяет подписки, истекающие через 3 дня, и создаёт заявки в Okdesk.
    Возвращает строку с результатом, либо логирует ошибки.
    """
    logger.info("Запуск задачи по расписанию.")
    try:
        now_time = datetime.datetime.now()
        target_date = (now_time + datetime.timedelta(days=3)).date()
        logger.info(f"Целевая дата для поиска истекающих подписок: {target_date}")

        # Получение активных подписок
        try:
            now_subs_services = crud.get_all_subs_from_time(now_time)
        except Exception as e:
            logger.error("Критическая ошибка при получении подписок из БД")
            return f"Ошибка получения подписок: {e}"

        if not now_subs_services:
            logger.info("Нет активных подписок, удовлетворяющих условию.")
            return "Нет активных подписок"

        logger.info(f"Получено {len(now_subs_services)} записей о подписках.")

        # Группировка истекающих объектов по ok_desk_id
        expiring_clients = defaultdict(lambda: {'company_name': '', 'objects': []})
        processed_count = 0  # количество записей, попавших под условие

        for sub in now_subs_services:
            try:
                ca_name = sub[0]
                sub_end = sub[1]
                ok_desk_id = sub[2]
                obj_name = sub[3]
                stealth_type = sub[4]

                if sub_end.date() == target_date:
                    expiring_clients[ok_desk_id]['company_name'] = ca_name
                    expiring_clients[ok_desk_id]['objects'].append({
                        'name': obj_name,
                        'type': stealth_type
                    })
                    processed_count += 1
            except (IndexError, TypeError, AttributeError) as e:
                logger.warning(f"Некорректная запись подписки, пропущена: {sub}. Ошибка: {e}")
                continue

        logger.info(f"Найдено {processed_count} объектов с истекающей подпиской, "
                    f"сгруппировано в {len(expiring_clients)} клиентов.")

        # Создание заявок для каждого клиента
        success_clients = 0
        for ok_desk_id, data in expiring_clients.items():
            if not ok_desk_id:
                logger.warning("Обнаружен пустой ok_desk_id, пропускаем клиента.")
                continue

            try:
                logger.info(f"Создаём заявку для клиента ID={ok_desk_id}, "
                             f"компания={data['company_name']}, объектов={len(data['objects'])}")
                create_iss_okdesk(
                    client_okdesk_id=ok_desk_id,
                    company_name=data['company_name'],
                    objects_list=data['objects']
                )
                success_clients += 1
                logger.info(f"Заявка для клиента {ok_desk_id} успешно создана.")
            except Exception as e:
                logger.error(f"Ошибка при создании заявки для клиента {ok_desk_id}")

        result = (f"Обработано клиентов с истекающей подпиской: {len(expiring_clients)}. "
                  f"Успешно создано заявок: {success_clients}")
        logger.info(result)
        return result

    except Exception as e:
        logger.error("Непредвиденная ошибка в задаче job()")
        return f"Глобальная ошибка: {e}"

# ---------- Планировщик ----------
if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Запуск планировщика. Задача запланирована ежедневно в 07:00.")
    schedule.every().day.at("07:00").do(job)

    # Бесконечный цикл с защитой от падения
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logger.error("Ошибка в основном цикле планировщика")
            # Можно добавить задержку перед продолжением
            time.sleep(60)
        time.sleep(30)  # проверка каждые 30 секунд
