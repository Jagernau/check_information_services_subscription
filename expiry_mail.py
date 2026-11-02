"""Письмо менеджерам об окончании подписки; настройки SMTP общие с оплатой."""
from html import escape

import config
from mailer import send_mail
from my_logger import logger


def send_expiry_mail(company_name, objects, manager_emails):
    to = sorted({str(a).strip().lower() for a in manager_emails if a and str(a).strip()})
    cc = sorted({a.strip().lower() for a in config.PAY_REMIND_CC if a.strip()} - set(to))
    subject = f"Окончание подписки на сервисы ({company_name})"
    lines = []
    rows = []
    # Один объект может встречаться несколько раз из-за соединений в БД.
    seen = set()
    for obj in objects:
        name = str(obj['name'] or '')
        tariff = {0: 'Premium', 1: 'VIP'}.get(obj['type'], 'Неизвестно')
        end = obj['end'].strftime('%d.%m.%Y')
        days = str(obj['days_left'])
        key = (name, tariff, end, days)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"{name} — {tariff}, окончание {end}, осталось дней: {days}")
        rows.append('<tr>' + ''.join(f'<td>{escape(v)}</td>' for v in key) + '</tr>')
    warning = ''
    if not to:
        warning = 'Менеджер или его email не указан в подписке. Укажите менеджера в биллинге.'
        logger.warning(f"{company_name}: {warning}")
    text = (f"У клиента {company_name} заканчивается подписка на сервисы. "
            "Необходимо согласовать продление.\n" + '\n'.join(lines) + '\n' + warning)
    body = (f'<p>У клиента <b>{escape(str(company_name))}</b> заканчивается подписка '
            'на сервисы. Необходимо согласовать продление.</p>'
            '<table border="1" cellpadding="8" cellspacing="0">'
            '<tr><th>Объект</th><th>Тариф</th><th>Окончание</th><th>Осталось дней</th></tr>'
            + ''.join(rows) + '</table>' + (f'<p>{escape(warning)}</p>' if warning else ''))
    if config.PAY_REMIND_TEST_TO:
        to, cc = [config.PAY_REMIND_TEST_TO], []
        subject = '[ТЕСТ] ' + subject
    send_mail(to, subject, body, cc=cc, text=text)
