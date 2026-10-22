"""Тесты напоминаний об оплате. Запуск из корня проекта: python -m pytest -q"""
from datetime import date, datetime

import pytest

import config
import pay_remind
from pay_remind import add_months, collect, due_pay_date, render


# ------------------------------------------------------------------ даты

def test_add_months_clips_to_month_end():
    assert add_months(date(2027, 1, 31), 1) == date(2027, 2, 28)
    assert add_months(date(2027, 1, 31), 2) == date(2027, 3, 31)
    assert add_months(date(2026, 9, 15), 4) == date(2027, 1, 15)


def reminder_days(start, end, days):
    """Первый день напоминания для каждой даты оплаты за всё время подписки."""
    first, d = {}, start
    while d <= end:
        due = due_pay_date(start, end, days, d)
        if due and due[0] not in first:
            first[due[0]] = d
        d = date.fromordinal(d.toordinal() + 1)
    return first


def test_pik_dates_every_11th():
    days = reminder_days(date(2026, 9, 15), date(2027, 3, 15), 4)
    assert days == {
        date(2026, 10, 15): date(2026, 10, 11),
        date(2026, 11, 15): date(2026, 11, 11),
        date(2026, 12, 15): date(2026, 12, 11),
        date(2027, 1, 15): date(2027, 1, 11),
        date(2027, 2, 15): date(2027, 2, 11),
    }   # 15.03 — конец подписки, платить дальше не за что


def test_window_until_pay_date_inclusive():
    start, end = date(2026, 9, 15), date(2027, 3, 15)
    assert due_pay_date(start, end, 4, date(2026, 11, 10)) is None
    assert due_pay_date(start, end, 4, date(2026, 11, 11)) == (date(2026, 11, 15), date(2026, 12, 15))
    assert due_pay_date(start, end, 4, date(2026, 11, 15))[0] == date(2026, 11, 15)
    assert due_pay_date(start, end, 4, date(2026, 11, 16)) is None


def test_start_on_31st():
    days = reminder_days(date(2027, 1, 31), date(2027, 5, 31), 4)
    assert days[date(2027, 2, 28)] == date(2027, 2, 24)
    assert days[date(2027, 4, 30)] == date(2027, 4, 26)


def test_last_month_paid_until_end():
    assert due_pay_date(date(2026, 9, 15), date(2027, 3, 1), 4, date(2027, 2, 11)) == \
        (date(2027, 2, 15), date(2027, 3, 1))


# ------------------------------------------------------------------ сборка

def row(sid, obj, ca_id=2310, start=datetime(2026, 9, 15), end=datetime(2027, 3, 15, 23, 59),
        manager=16, email="manager@example.com", tarif="VIP-8-6", days=4):
    return {"serv_obj_id": sid, "ca_id": ca_id, "ca_name": f"Клиент {ca_id} <ООО>",
            "ok_desk_id": 818, "object_name": obj, "tarif_name": tarif,
            "subscription_start": start, "subscription_end": end,
            "pay_remind_days": days, "pay_remind_manager_id": manager,
            "manager_first_name": "Антон", "manager_last_name": "Скрипкин",
            "manager_email": email}


def test_collect_groups_objects_and_skips_duplicates():
    rows = [row(1, "А001АА152"), row(2, "А001АА152"), row(3, "В002ВВ152"), row(3, "В002ВВ152")]
    rems = collect(rows, date(2026, 11, 12))
    assert len(rems) == 1
    rem = rems[0]
    assert rem.pay_date == date(2026, 11, 15)
    sub, until = rem.items[0]
    assert sub.objects == {"А001АА152", "В002ВВ152"} and sub.services == 3
    assert until == date(2026, 12, 15)
    assert rem.manager_emails == ["manager@example.com"]


def test_collect_nothing_outside_window():
    assert collect([row(1, "А001АА152")], date(2026, 11, 20)) == []


def test_render_escapes_names():
    rem = collect([row(1, "<b>ТС</b>")], date(2026, 11, 11))[0]
    subject, body, _ = render(rem)
    assert "15.11.2026" in subject
    assert "&lt;ООО&gt;" in body and "&lt;b&gt;ТС&lt;/b&gt;" in body
    assert "Скрипкин Антон" in body


def test_render_without_manager():
    rem = collect([row(1, "А001АА152", manager=None, email=None)], date(2026, 11, 11))[0]
    assert rem.manager_emails == []
    assert "не указан" in render(rem)[1]


# ------------------------------------------------------------------ run()

class FakeSession:
    def close(self): pass
    def rollback(self): pass


class FakeDb:
    def __init__(self):
        self.session = FakeSession()
        self.engine = type("E", (), {"dispose": lambda self: None})()


@pytest.fixture
def env(monkeypatch):
    state = {"rows": [row(1, "А001АА152"), row(2, "В002ВВ152")], "log": {},
             "mails": [], "issues": [], "mail_fail": False}

    monkeypatch.setattr(pay_remind, "MysqlDatabase", FakeDb)
    monkeypatch.setattr(pay_remind.rcrud, "get_remind_subscriptions",
                        lambda s, day: state["rows"])

    def get_or_create_log(s, ca_id, pay_date):
        return dict(state["log"].setdefault(
            (ca_id, pay_date), {"id": len(state["log"]) + 1,
                                "mail_sent_at": None, "okdesk_issue_id": None}))

    def find(log_id):
        return next(v for v in state["log"].values() if v["id"] == log_id)

    monkeypatch.setattr(pay_remind.rcrud, "get_or_create_log", get_or_create_log)
    monkeypatch.setattr(pay_remind.rcrud, "set_mail_sent",
                        lambda s, i, to: find(i).update(mail_sent_at=datetime.now(), mail_to=to))
    monkeypatch.setattr(pay_remind.rcrud, "set_okdesk_issue",
                        lambda s, i, iid: find(i).update(okdesk_issue_id=iid))

    def send_mail(to, subject, html, cc=(), text=""):
        if state["mail_fail"]:
            raise OSError("SMTP недоступен")
        state["mails"].append({"to": list(to), "cc": list(cc), "subject": subject})
    monkeypatch.setattr(pay_remind, "send_mail", send_mail)

    class FakeOk:
        def __init__(self, *a): pass
        def get_all_employ(self):
            return [{"id": 77, "email": "Manager@Example.com", "active": True}]
        def create_issues(self, **kw):
            state["issues"].append(kw)
            return {"id": 5000 + len(state["issues"])}
    monkeypatch.setattr(pay_remind, "OkdeskClass", FakeOk)

    monkeypatch.setattr(config, "PAY_REMIND_CC", ["td@example.com", "me@example.com"])
    monkeypatch.setattr(config, "PAY_REMIND_TEST_TO", "")
    monkeypatch.setattr(config, "PAY_REMIND_OK_TYPE", "pay_remind")
    return state


def test_run_sends_once_and_assigns_manager(env):
    pay_remind.run(date(2026, 11, 11))
    assert env["mails"] == [{"to": ["manager@example.com"],
                             "cc": ["td@example.com", "me@example.com"],
                             "subject": env["mails"][0]["subject"]}]
    issue = env["issues"][0]
    assert issue["assignee_id"] == "77" and issue["company_id"] == "818"
    assert issue["type_iss"] == "pay_remind" and issue["deadline_at"] == "2026-11-15 17:30"

    pay_remind.run(date(2026, 11, 12))          # на следующий день — ничего нового
    assert len(env["mails"]) == 1 and len(env["issues"]) == 1


def test_run_retries_mail_next_day(env):
    env["mail_fail"] = True
    lines = pay_remind.run(date(2026, 11, 11))
    assert not env["mails"] and len(env["issues"]) == 1
    assert any("повторю завтра" in x for x in lines)
    env["mail_fail"] = False
    pay_remind.run(date(2026, 11, 12))
    assert len(env["mails"]) == 1 and len(env["issues"]) == 1


def test_run_dry_and_test_mode_write_nothing(env, monkeypatch):
    lines = pay_remind.run(date(2026, 11, 11), dry=True)
    assert not env["mails"] and not env["issues"] and not env["log"]
    assert any("manager@example.com" in x for x in lines)

    monkeypatch.setattr(config, "PAY_REMIND_TEST_TO", "tester@example.com")
    pay_remind.run(date(2026, 11, 11))
    assert env["mails"][0]["to"] == ["tester@example.com"] and env["mails"][0]["cc"] == []
    assert env["mails"][0]["subject"].startswith("[ТЕСТ]")
    assert not env["issues"] and not env["log"]


def test_run_test_mode_skips_manager_and_journal(env, monkeypatch):
    monkeypatch.setattr(config, "PAY_REMIND_OK_ASSIGNEE", "2")
    lines = pay_remind.run(date(2026, 11, 11), test=True)
    assert env["mails"] == [{"to": ["td@example.com", "me@example.com"], "cc": [],
                             "subject": env["mails"][0]["subject"]}]
    assert env["mails"][0]["subject"].startswith("[ТЕСТ]")
    issue = env["issues"][0]
    assert issue["title"].startswith("[ТЕСТ]") and issue["assignee_id"] == "2"
    assert issue["company_id"] == "818"
    assert not env["log"]                                # журнал не тронут
    assert any("менеджеру не отправлялось" in x for x in lines)

    pay_remind.run(date(2026, 11, 11))                   # настоящий запуск после теста
    assert env["mails"][1]["to"] == ["manager@example.com"]
    assert env["issues"][1]["assignee_id"] == "77"
