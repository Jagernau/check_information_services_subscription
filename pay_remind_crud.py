"""Запросы к БД для ежемесячных напоминаний об оплате.

Колонки info_serv_obj.pay_remind_days / pay_remind_manager_id и таблица
info_serv_pay_remind_log добавлены отдельно от mysql_models.py, поэтому здесь
обычный SQL, а модели трогать не нужно.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

SUBSCRIPTIONS_SQL = text("""
    SELECT o.serv_obj_id, c.ca_id, c.ca_name, c.ok_desk_id,
           co.object_name, t.name AS tarif_name,
           o.subscription_start, o.subscription_end,
           o.pay_remind_days, o.pay_remind_manager_id,
           u.first_name AS manager_first_name, u.last_name AS manager_last_name,
           u.email AS manager_email
    FROM info_serv_obj o
    JOIN Login_users l ON l.login = o.sys_login
                      AND l.password = o.sys_password
                      AND l.system_id = o.monitoring_sys
    JOIN Contragents c ON c.ca_id = l.contragent_id
    JOIN ca_objects co ON co.id = o.serv_obj_sys_mon_id
    LEFT JOIN info_serv_tarifs t ON t.tarif_id = o.info_serv_tarif_id
    LEFT JOIN auth_user u ON u.id = o.pay_remind_manager_id
    WHERE o.pay_remind_days IS NOT NULL
      AND o.subscription_start < :day_after
      AND o.subscription_end >= :day
""")


def get_remind_subscriptions(session, day: date) -> list:
    """Строки подписок с включённым напоминанием, действующие в этот день."""
    return session.execute(SUBSCRIPTIONS_SQL, {
        "day": day, "day_after": day + timedelta(days=1)}).mappings().all()


def get_log(session, ca_id: int, pay_date: date):
    """Запись журнала по клиенту и дате оплаты или None."""
    return session.execute(text(
        "SELECT id, mail_sent_at, okdesk_issue_id FROM info_serv_pay_remind_log "
        "WHERE contragent_id = :ca AND pay_date = :d"),
        {"ca": ca_id, "d": pay_date}).mappings().first()


def get_or_create_log(session, ca_id: int, pay_date: date):
    """Запись журнала; если её нет — создаёт пустую (ничего ещё не отправлено)."""
    row = get_log(session, ca_id, pay_date)
    if row is None:
        try:
            session.execute(text(
                "INSERT INTO info_serv_pay_remind_log (contragent_id, pay_date) "
                "VALUES (:ca, :d)"), {"ca": ca_id, "d": pay_date})
            session.commit()
        except IntegrityError:      # запись успели создать параллельно
            session.rollback()
        row = get_log(session, ca_id, pay_date)
    return row


def set_mail_sent(session, log_id: int, mail_to: str) -> None:
    session.execute(text(
        "UPDATE info_serv_pay_remind_log SET mail_to = :to, mail_sent_at = NOW() "
        "WHERE id = :id"), {"to": mail_to[:500], "id": log_id})
    session.commit()


def set_okdesk_issue(session, log_id: int, issue_id: int) -> None:
    session.execute(text(
        "UPDATE info_serv_pay_remind_log SET okdesk_issue_id = :iid WHERE id = :id"),
        {"iid": issue_id, "id": log_id})
    session.commit()
