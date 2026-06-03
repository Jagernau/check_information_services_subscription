from db_conectors import MysqlDatabase
import mysql_models as models
from sqlalchemy import and_, func
from my_logger import logger as log


def get_all_subs_from_time(date_time):
    """
    Возвращает подписки, для которых сегодня нужно отправить уведомление:
    - подписка активна на текущий момент (subscription_start <= date_time <= subscription_end)
    - количество дней до окончания равно subs_day_send (не NULL)
    """
    db = MysqlDatabase()
    session = db.session
    try:
        result = (
            session.query(
                models.Contragents.ca_name,
                models.InfoServObj.subscription_end,
                models.Contragents.ok_desk_id,
                models.CaObjects.object_name,
                models.InfoServObj.stealth_type,
                models.InfoServObj.subs_day_send          # добавили поле
            )
            .select_from(models.InfoServObj)
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
                models.InfoServObj.subscription_end >= date_time,
                models.InfoServObj.subs_day_send.isnot(None),
                func.datediff(models.InfoServObj.subscription_end, date_time) == models.InfoServObj.subs_day_send
            )
            .group_by(
                models.Contragents.ca_name,
                models.InfoServObj.subscription_end,
                models.Contragents.ok_desk_id,
                models.CaObjects.object_name,
                models.InfoServObj.stealth_type,
                models.InfoServObj.subs_day_send
            )
            .all()
        )
        return result
    except Exception as e:
        log.error(f"Ошибка при получении подписок для оповещения: {e}")
        return None
    finally:
        session.close()

