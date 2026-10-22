"""Ежемесячные напоминания менеджерам по продажам об оплате сервисов.

Клиент платит помесячно, хотя подписка оформлена на несколько месяцев.
Каждый месяц в то же число, что начало подписки (15.09 → 15.10, 15.11 …),
начинается очередной оплачиваемый месяц. За pay_remind_days дней до этой даты
закреплённый менеджер получает письмо (копия — PAY_REMIND_CC), а в ОКДЕСК
создаётся заявка на компанию клиента с менеджером в ответственных.

Что включено и кто менеджер — в info_serv_obj (pay_remind_days,
pay_remind_manager_id), ставится в billing_web. Что уже отправлено —
в info_serv_pay_remind_log: одна запись на клиента и дату оплаты, поэтому
повторно не шлётся, а если в день напоминания программа не работала или упала
почта/ОКДЕСК, недостающее дошлётся в следующие дни, до даты оплаты включительно.
"""
from __future__ import annotations

import calendar
import html
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import config
import pay_remind_crud as rcrud
from db_conectors import MysqlDatabase
from mailer import send_mail
from my_logger import logger
from okdesc_class import OkdeskClass


# ------------------------------------------------------------------ даты

def add_months(d: date, months: int) -> date:
    """То же число через months месяцев; 31.01 + 1 мес = 28.02 (29.02)."""
    m = d.month - 1 + months
    y, m = d.year + m // 12, m % 12 + 1
    return d.replace(year=y, month=m, day=min(d.day, calendar.monthrange(y, m)[1]))


def due_pay_date(start: date, end: date, days: int,
                 today: date) -> Optional[Tuple[date, date]]:
    """Дата оплаты, о которой сегодня пора напомнить, и до какого числа она оплачивает.

    Даты оплаты — start + 1, 2, 3 … месяца. Напоминаем с (дата − days) по саму дату
    включительно. Дата, в которую подписка уже заканчивается, не считается.
    Возвращает None, если сегодня напоминать не о чем.
    """
    k = 1
    while True:
        pay = add_months(start, k)
        if pay >= end:
            return None
        if pay - timedelta(days=days) <= today <= pay:
            return pay, min(add_months(start, k + 1), end)
        if pay > today:
            return None
        k += 1


# ------------------------------------------------------------------ сборка

@dataclass
class Subscription:
    """Подписка как строка в billing (/serv_contragents): клиент + тариф + период."""
    ca_id: int
    ca_name: str
    ok_desk_id: Optional[int]
    tarif: str
    start: datetime
    end: datetime
    days: int
    manager_id: Optional[int]
    manager_name: str
    manager_email: str
    objects: set = field(default_factory=set)
    services: int = 0


@dataclass
class Reminder:
    """Одно напоминание: клиент + дата оплаты (может включать несколько подписок)."""
    ca_id: int
    ca_name: str
    ok_desk_id: Optional[int]
    pay_date: date
    items: List[Tuple[Subscription, date]] = field(default_factory=list)

    @property
    def managers(self) -> List[Tuple[str, str]]:
        """(ФИО, почта) менеджеров без повторов."""
        seen, out = set(), []
        for sub, _ in self.items:
            key = (sub.manager_name, sub.manager_email)
            if sub.manager_id and key not in seen:
                seen.add(key)
                out.append(key)
        return out

    @property
    def manager_emails(self) -> List[str]:
        return [e for _, e in self.managers if e]


def collect(rows, today: date) -> List[Reminder]:
    """Из строк info_serv_obj собирает напоминания, которые пора отправить сегодня."""
    subs: Dict[tuple, Subscription] = {}
    seen_ids = set()
    for r in rows:
        if r["serv_obj_id"] in seen_ids:       # дубли от нескольких Login_users
            continue
        seen_ids.add(r["serv_obj_id"])
        key = (r["ca_id"], r["tarif_name"], r["subscription_start"],
               r["subscription_end"], r["pay_remind_days"], r["pay_remind_manager_id"])
        sub = subs.get(key)
        if sub is None:
            name = " ".join(p for p in (r["manager_last_name"], r["manager_first_name"]) if p)
            sub = subs[key] = Subscription(
                ca_id=r["ca_id"], ca_name=r["ca_name"] or "", ok_desk_id=r["ok_desk_id"],
                tarif=r["tarif_name"] or "без тарифа",
                start=r["subscription_start"], end=r["subscription_end"],
                days=int(r["pay_remind_days"]), manager_id=r["pay_remind_manager_id"],
                manager_name=name, manager_email=(r["manager_email"] or "").strip())
        sub.objects.add(r["object_name"] or "")
        sub.services += 1

    reminders: Dict[tuple, Reminder] = {}
    for sub in subs.values():
        due = due_pay_date(sub.start.date(), sub.end.date(), sub.days, today)
        if not due:
            continue
        pay, paid_until = due
        rem = reminders.get((sub.ca_id, pay))
        if rem is None:
            rem = reminders[(sub.ca_id, pay)] = Reminder(
                sub.ca_id, sub.ca_name, sub.ok_desk_id, pay)
        rem.items.append((sub, paid_until))
    return sorted(reminders.values(), key=lambda x: (x.pay_date, x.ca_name))


# ------------------------------------------------------------------ текст

def _d(x) -> str:
    return x.strftime("%d.%m.%Y")


def render(rem: Reminder) -> Tuple[str, str, str]:
    """(тема, HTML, текст) письма; HTML же идёт в описание заявки ОКДЕСК."""
    e = html.escape
    subject = f"Договор на сервисы: {rem.ca_name} — оплата с {_d(rem.pay_date)}"
    rows = "".join(f"""
        <tr>
          <td style="padding:6px 10px;border:1px solid #ddd">{e(sub.tarif)}</td>
          <td style="padding:6px 10px;border:1px solid #ddd;text-align:center">{len(sub.objects)}</td>
          <td style="padding:6px 10px;border:1px solid #ddd">{_d(sub.start)} – {_d(sub.end)}</td>
          <td style="padding:6px 10px;border:1px solid #ddd"><b>{_d(rem.pay_date)} – {_d(until)}</b></td>
        </tr>""" for sub, until in rem.items)
    objects = sorted({o for sub, _ in rem.items for o in sub.objects if o})
    managers = ", ".join(e(n) for n, _ in rem.managers) or \
        '<span style="color:#d93025">не указан — выберите менеджера в биллинге</span>'
    body = f"""
<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#202124;max-width:720px">
  <p>Добрый день!</p>
  <p><b>{_d(rem.pay_date)}</b> у клиента <b>{e(rem.ca_name)}</b> начинается следующий
     оплачиваемый месяц по сервисам. Нужно заключить с клиентом договор на этот месяц.</p>
  <table style="border-collapse:collapse;margin:12px 0">
    <tr style="background:#f1f3f4">
      <th style="padding:6px 10px;border:1px solid #ddd;text-align:left">Тариф</th>
      <th style="padding:6px 10px;border:1px solid #ddd">ТС</th>
      <th style="padding:6px 10px;border:1px solid #ddd;text-align:left">Подписка</th>
      <th style="padding:6px 10px;border:1px solid #ddd;text-align:left">Следующий месяц</th>
    </tr>{rows}
  </table>
  <p>Менеджер: {managers}</p>
  <p style="font-size:12px;color:#5f6368">ТС ({len(objects)}): {e(", ".join(objects))}</p>
  <p style="font-size:12px;color:#5f6368">Письмо отправлено автоматически. Напоминание
     включается и выключается в биллинге, на странице «Управление сервисами».</p>
</div>"""
    text_body = (f"{_d(rem.pay_date)} у клиента {rem.ca_name} начинается следующий "
                 f"оплачиваемый месяц по сервисам. Нужно заключить договор на этот месяц.")
    return subject, body, text_body


# ------------------------------------------------------------------ отправка

def _okdesk_employees(ok: OkdeskClass) -> Dict[str, int]:
    """почта сотрудника ОКДЕСК → его id."""
    out = {}
    for emp in ok.get_all_employ() or []:
        mail = str(emp.get("email") or "").strip().lower()
        if mail and emp.get("active", True) and emp.get("id"):
            out[mail] = emp["id"]
    return out


def run(today: Optional[date] = None, dry: bool = False, test: bool = False) -> List[str]:
    """Проверяет и отправляет напоминания на дату today (по умолчанию сегодня).

    dry=True  — только показать, что ушло бы, ничего не отправляя и не записывая.
    test=True — отправить по-настоящему, но без менеджера: письмо только на
                PAY_REMIND_CC, заявка в ОКДЕСК с пометкой [ТЕСТ] на ответственного
                по умолчанию (PAY_REMIND_OK_ASSIGNEE). В журнал ничего не пишется,
                поэтому настоящее напоминание потом уйдёт как обычно.
    Возвращает строки-итоги (они же пишутся в лог).
    """
    today = today or date.today()
    test_to = config.PAY_REMIND_TEST_TO
    result: List[str] = []

    def note(msg: str, level: str = "info") -> None:
        getattr(logger, level)(f"Напоминания об оплате: {msg}")
        result.append(msg)

    okdesk = {}     # клиент ОКДЕСК и его сотрудники — заводятся при первой заявке

    def create_issue(rem: Reminder, body: str, who: str, log_id: Optional[int],
                     is_test: bool = False) -> None:
        if not rem.ok_desk_id:
            note(f"{who}: у клиента нет ok_desk_id, заявку не создать", "warning")
            return
        if not okdesk:
            okdesk["api"] = OkdeskClass(config.OK_URL, config.OK_TOKEN)
            okdesk["employees"] = {} if is_test else _okdesk_employees(okdesk["api"])
        employees = okdesk["employees"]
        assignee = next((employees[m.lower()] for m in rem.manager_emails
                         if m.lower() in employees), config.PAY_REMIND_OK_ASSIGNEE)
        title = f"Заключить договор на сервисы с {_d(rem.pay_date)} ({rem.ca_name})"
        resp = okdesk["api"].create_issues(
            title=("[ТЕСТ] " if is_test else "") + title,
            description=body,
            company_id=str(rem.ok_desk_id),
            assignee_id=str(assignee),
            maintenance_entity_id=None,
            type_iss=config.PAY_REMIND_OK_TYPE,
            deadline_at=f"{rem.pay_date:%Y-%m-%d} 17:30",
        )
        if resp and resp.get("id"):
            if log_id:
                rcrud.set_okdesk_issue(session, log_id, int(resp["id"]))
            note(f"{who}: заявка ОКДЕСК {resp['id']}, ответственный {assignee}")
        else:
            note(f"{who}: ОКДЕСК не создал заявку" + ("" if is_test else ", повторю завтра"),
                 "error")

    def process(rem: Reminder) -> None:
        subject, body, text_body = render(rem)
        to, cc = rem.manager_emails, config.PAY_REMIND_CC
        who = f"{rem.ca_name}, оплата с {_d(rem.pay_date)}"
        if dry:
            note(f"{who}: письмо → {', '.join(to) or 'менеджер не указан'} "
                 f"(копия {', '.join(cc)}); заявка в ОКДЕСК на компанию {rem.ok_desk_id}")
            return
        if test:
            managers = ", ".join(f"{n} {e}".strip() for n, e in rem.managers) or "не указан"
            body = (f'<div style="font-family:Arial,sans-serif;font-size:13px;background:#fef7e0;'
                    f'border-left:4px solid #f4b400;padding:8px 12px;margin-bottom:12px">'
                    f'<b>Тестовая отправка.</b> Менеджеру ({html.escape(managers)}) не отправлялось.'
                    f'</div>') + body
            try:
                send_mail(cc, "[ТЕСТ] " + subject, body, text=text_body)
                note(f"{who}: тестовое письмо → {', '.join(cc)} (менеджеру не отправлялось)")
            except Exception as e:
                note(f"{who}: тестовое письмо не ушло: {e}", "error")
            if config.PAY_REMIND_OK_TYPE:
                try:
                    create_issue(rem, body, who, None, is_test=True)
                except Exception as e:
                    note(f"{who}: тестовая заявка в ОКДЕСК не создана: {e}", "error")
            return
        if test_to:
            send_mail([test_to], "[ТЕСТ] " + subject, body, text=text_body)
            note(f"{who}: тестовое письмо → {test_to}")
            return

        log = rcrud.get_or_create_log(session, rem.ca_id, rem.pay_date)
        if log["mail_sent_at"] is None:
            try:
                send_mail(to, subject, body, cc=cc, text=text_body)
                rcrud.set_mail_sent(session, log["id"], ", ".join(to + cc))
                note(f"{who}: письмо → {', '.join(to + cc)}")
            except Exception as e:
                session.rollback()
                note(f"{who}: письмо не ушло, повторю завтра: {e}", "error")
        if log["okdesk_issue_id"] is None and config.PAY_REMIND_OK_TYPE:
            try:
                create_issue(rem, body, who, log["id"])
            except Exception as e:
                session.rollback()
                note(f"{who}: заявка в ОКДЕСК не создана, повторю завтра: {e}", "error")

    db = MysqlDatabase()
    session = db.session
    try:
        reminders = collect(rcrud.get_remind_subscriptions(session, today), today)
        mode = (" (проверка, ничего не отправляется)" if dry else
                " (тест: без менеджера, заявка с пометкой [ТЕСТ], журнал не трогаю)" if test else
                f" (тестовый режим, всё на {test_to})" if test_to else "")
        note(f"{_d(today)} — к отправке {len(reminders)}{mode}")
        for rem in reminders:
            try:
                process(rem)
            except Exception as e:
                session.rollback()
                note(f"{rem.ca_name}, оплата с {_d(rem.pay_date)}: ошибка {e}", "error")
    except Exception as e:
        note(f"ошибка: {e}", "error")
    finally:
        session.close()
        db.engine.dispose()
    return result


def job():
    """Ежедневный запуск из планировщика."""
    try:
        run()
    except Exception as e:      # планировщик не должен падать
        logger.error(f"Напоминания об оплате: непредвиденная ошибка {e}")
