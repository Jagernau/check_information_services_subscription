from db_conectors import MysqlDatabase
import mysql_models as models
from sqlalchemy import and_
from my_logger import logger as log


def get_all_subs_from_time(date_time):
    "Отдаёт актуальные подписки на сегодня"
    db = MysqlDatabase()
    session = db.session
    try:
        result = (
            session.query(models.Contragents.ca_name, models.InfoServObj.subscription_end, models.Contragents.ok_desk_id, models.CaObjects.object_name, models.InfoServObj.stealth_type)
            .select_from(models.InfoServObj)               # ← явно указываем стартовую таблицу
            .join(
                models.LoginUsers,
                and_(
                    models.InfoServObj.sys_login == models.LoginUsers.login,
                    models.InfoServObj.sys_password == models.LoginUsers.password,
                    models.InfoServObj.monitoring_sys == models.LoginUsers.system_id
                )
            )
            .join(
                models.Contragents,
                models.LoginUsers.contragent_id == models.Contragents.ca_id
            )
            .join(
                models.CaObjects,
                models.InfoServObj.serv_obj_sys_mon_id == models.CaObjects.id
            )
            .filter(
                models.InfoServObj.subscription_start <= date_time,
                models.InfoServObj.subscription_end >= date_time
            )
            .group_by(models.Contragents.ca_name, models.InfoServObj.subscription_end, models.Contragents.ok_desk_id, models.CaObjects.object_name, models.InfoServObj.stealth_type)
            .all()
        )
        return result

    except Exception as e:
        log.error(f"Ошибка при получении подписок: {e}")
        return None

    finally:
        session.close()

