"""Отправка писем через SMTP — так же, как в mail_sender (STARTTLS + логин)."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Iterable

import config


def send_mail(to: Iterable[str], subject: str, html: str, cc: Iterable[str] = (),
              text: str = "") -> None:
    """Отправляет HTML-письмо. Ошибку не глотает — решает вызывающий."""
    to, cc = [a for a in to if a], [a for a in cc if a]
    if not to and not cc:
        raise ValueError("Нет ни одного получателя")
    msg = EmailMessage()
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = ", ".join(to or cc)
    if to and cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject
    msg.set_content(text or "Письмо в формате HTML.")
    msg.add_alternative(html, subtype="html")
    # SMTP_SERVER может быть «host» или «host:port», smtplib понимает оба
    with smtplib.SMTP(config.SMTP_SERVER, timeout=60) as server:
        server.starttls()
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        server.send_message(msg)
