from db_conectors import MysqlDatabase
import mysql_models as models
from sqlalchemy import and_, func, literal_column, or_
from sqlalchemy.orm import aliased
from my_logger import logger as log


def _manager_join_and_email():
    """Возвращает (KeyUser alias, SubUser alias, выражение выбора email)."""
    KeyUser = aliased(models.AuthUser)
    SubUser = aliased(models.AuthUser)
    manager_email = func.coalesce(
        func.nullif(func.trim(KeyUser.email), ''),
        func.nullif(func.trim(SubUser.email), '')
    )
    return KeyUser, SubUser, manager_email


def _key_manager_condition(KeyUser):
    """Условие сопоставления Contragents.key_manager ('Фамилия Имя Отчество') с auth_user."""
    full_name_space = KeyUser.last_name + ' ' + KeyUser.first_name
    return and_(
        models.Contragents.key_manager.isnot(None),
        func.trim(models.Contragents.key_manager) != '',
        KeyUser.last_name != '',
        or_(
            func.trim(models.Contragents.key_manager) == full_name_space,
            func.trim(models.Contragents.key_manager).like(full_name_space + ' %'),
            func.trim(models.Contragents.key_manager) == KeyUser.username,
            func.trim(models.Contragents.key_manager) == KeyUser.email,
        )
    )


def get_all_subs_from_time(date_time):
    """
    Возвращает подписки, для которых сегодня нужно отправить уведомление:
    - подписка активна на текущий момент (subscription_start <= date_time <= subscription_end)
    - количество дней до окончания равно subs_day_send (не NULL)
    """
    db = MysqlDatabase()
    session = db.session
    try:
        KeyUser, SubUser, manager_email = _manager_join_and_email()
        result = (
            session.query(
                models.Contragents.ca_name,
                models.InfoServObj.subscription_end,
                models.Contragents.ok_desk_id,
                models.CaObjects.object_name,
                models.InfoServObj.stealth_type,
                models.InfoServObj.subs_day_send,
                manager_email
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
            .outerjoin(KeyUser, _key_manager_condition(KeyUser))
            .outerjoin(
                SubUser,
                SubUser.id == literal_column("info_serv_obj.pay_remind_manager_id")
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
                models.InfoServObj.subs_day_send,
                manager_email
            )
            .all()
        )
        return result
    except Exception as e:
        log.error(f"Ошибка при получении подписок для оповещения: {e}")
        return None
    finally:
        session.close()


def get_subs_for_client_okdesk(ok_desk_id: int, date_time):
    """
    Возвращает действующие подписки конкретного клиента по ok_desk_id
    независимо от того, сколько дней осталось до окончания (для тестового запуска).
    """
    db = MysqlDatabase()
    session = db.session
    try:
        KeyUser, SubUser, manager_email = _manager_join_and_email()
        days_left_expr = func.datediff(models.InfoServObj.subscription_end, date_time)
        result = (
            session.query(
                models.Contragents.ca_name,
                models.InfoServObj.subscription_end,
                models.Contragents.ok_desk_id,
                models.CaObjects.object_name,
                models.InfoServObj.stealth_type,
                days_left_expr,
                manager_email
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
            .outerjoin(KeyUser, _key_manager_condition(KeyUser))
            .outerjoin(
                SubUser,
                SubUser.id == literal_column("info_serv_obj.pay_remind_manager_id")
            )
            .filter(
                models.Contragents.ok_desk_id == ok_desk_id,
                models.InfoServObj.subscription_end >= date_time,
            )
            .group_by(
                models.Contragents.ca_name,
                models.InfoServObj.subscription_end,
                models.Contragents.ok_desk_id,
                models.CaObjects.object_name,
                models.InfoServObj.stealth_type,
                days_left_expr,
                manager_email
            )
            .all()
        )
        return result
    except Exception as e:
        log.error(f"Ошибка при получении подписок клиента {ok_desk_id}: {e}")
        return None
    finally:
        session.close()