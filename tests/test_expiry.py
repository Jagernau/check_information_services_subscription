from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

import config
import crud
import expiry_mail
import main
import okdesk_handler


@pytest.fixture
def env(monkeypatch):
    rows = [('Клиент <ООО>', datetime(2026, 11, 9), 818, '<ТС>', 1, 7,
             ' Manager@Example.com ')]
    monkeypatch.setattr(config, 'PAY_REMIND_TEST_TO', '')
    monkeypatch.setattr(config, 'PAY_REMIND_CC', ['td@example.com', 'me@example.com'])
    monkeypatch.setattr(main.crud, 'get_all_subs_from_time', lambda now: rows)
    mail, issue = Mock(), Mock(return_value={'id': 5000})
    monkeypatch.setattr(expiry_mail, 'send_mail', mail)
    monkeypatch.setattr(main, 'create_iss_okdesk', issue)
    return rows, mail, issue


def test_expiry_sends_manager_and_cc(env):
    rows, mail, issue = env
    rows.append((*rows[0][:6], 'second@example.com'))
    result = main.job()
    issue.assert_called_once()
    mail.assert_called_once()
    assert mail.call_args.args[0] == ['manager@example.com', 'second@example.com']
    assert mail.call_args.kwargs['cc'] == ['me@example.com', 'td@example.com']
    body = mail.call_args.args[2]
    assert '&lt;ООО&gt;' in body and body.count('&lt;ТС&gt;') == 1
    assert '09.11.2026' in body and 'VIP' in body
    assert 'Успешно создано заявок: 1. Отправлено писем: 1' in result


def test_missing_manager_still_sends_cc(env):
    rows, mail, _ = env
    rows[0] = (*rows[0][:6], None)
    main.job()
    assert mail.call_args.args[0] == []
    assert len(mail.call_args.kwargs['cc']) == 2
    assert 'не указан' in mail.call_args.args[2]


@pytest.mark.parametrize('failed_channel', ['mail', 'issue'])
def test_channel_failure_does_not_block_other_clients(env, failed_channel):
    rows, mail, issue = env
    rows.append(('Другой клиент', *rows[0][1:2], 819, *rows[0][3:]))
    failed = mail if failed_channel == 'mail' else issue
    failed.side_effect = [RuntimeError('unavailable'), {'id': 5001}]
    result = main.job()
    assert mail.call_count == issue.call_count == 2
    assert ('Отправлено писем: 1' if failed_channel == 'mail'
            else 'Успешно создано заявок: 1') in result


def test_test_address_suppresses_real_recipients_and_okdesk(env, monkeypatch):
    _, mail, issue = env
    monkeypatch.setattr(config, 'PAY_REMIND_TEST_TO', 'test@example.com')
    main.job()
    issue.assert_not_called()
    assert mail.call_args.args[0] == ['test@example.com']
    assert mail.call_args.kwargs['cc'] == []
    assert mail.call_args.args[1].startswith('[ТЕСТ]')


def test_no_subscriptions(env):
    rows, mail, issue = env
    rows.clear()
    main.job()
    mail.assert_not_called()
    issue.assert_not_called()


@pytest.mark.parametrize('response', [None, {}, {'errors': ['invalid']}, {'id': 5000}])
def test_okdesk_result_is_validated(monkeypatch, response):
    api = Mock()
    api.create_issues.return_value = response
    monkeypatch.setattr(okdesk_handler, 'OkdeskClass', lambda *args: api)
    if response and response.get('id'):
        assert okdesk_handler.create_iss_okdesk(818, 'Клиент', [], 7) == response
    else:
        with pytest.raises(RuntimeError):
            okdesk_handler.create_iss_okdesk(818, 'Клиент', [], 7)


def test_query_keeps_expiring_subscriptions_without_monthly_reminders(monkeypatch):
    engine = create_engine('sqlite://')
    @event.listens_for(engine, 'connect')
    def add_sqlite_functions(connection, record):
        connection.create_function('datediff', 2, lambda end, now:
                                  (datetime.fromisoformat(end).date() -
                                   datetime.fromisoformat(now).date()).days)
        connection.create_function('concat', -1, lambda *args: ''.join(str(arg) for arg in args if arg is not None))
    with engine.begin() as c:
        for sql in [
            'CREATE TABLE info_serv_obj (sys_login TEXT, sys_password TEXT, monitoring_sys INT, '
            'serv_obj_sys_mon_id INT, subscription_start DATETIME, subscription_end DATETIME, '
            'stealth_type INT, subs_day_send INT, pay_remind_manager_id INT, pay_remind_days INT)',
            'CREATE TABLE Login_users (login TEXT, password TEXT, system_id INT, contragent_id INT)',
            'CREATE TABLE Contragents (ca_id INT, ca_name TEXT, ok_desk_id INT, key_manager TEXT)',
            'CREATE TABLE ca_objects (id INT, object_name TEXT)',
            'CREATE TABLE auth_user (id INT, username TEXT, first_name TEXT, last_name TEXT, email TEXT)',
            "INSERT INTO Login_users VALUES ('login', 'password', 1, 5)",
            "INSERT INTO Contragents VALUES (5, 'ДИРЕКЦИЯ ПО ОРГАНИЗАЦИИ ПИТАНИЯ МБУ (ЭДО)', 472, 'Скрипкин Антон Владимирович')",
            "INSERT INTO ca_objects VALUES (1, 'Vehicle')",
            "INSERT INTO auth_user VALUES (16, 'skripkin', 'Антон', 'Скрипкин', 'skripkin@suntel-nn.ru')",
            "INSERT INTO info_serv_obj VALUES ('login', 'password', 1, 1, '2026-09-01', "
            "'2026-11-09', 1, 7, NULL, NULL)",
        ]:
            c.exec_driver_sql(sql)
    monkeypatch.setattr(crud, 'MysqlDatabase', lambda: SimpleNamespace(session=Session(engine)))
    rows = crud.get_all_subs_from_time(datetime(2026, 11, 2))
    assert len(rows) == 1
    assert rows[0][6] == 'skripkin@suntel-nn.ru'
    engine.dispose()
