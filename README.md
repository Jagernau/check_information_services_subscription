# check_information_services_subscription

Фоновая программа, которая каждый день проверяет подписки клиентов на информационные сервисы (таблица `info_serv_obj` в базе `suntel`) и рассылает оповещения:

1. **Клиенту — об окончании подписки.** Каждый день в 07:00 создаёт заявку в ОКДЕСК на компанию клиента, если до конца подписки осталось столько дней, сколько указано в подписке (`subs_day_send`, обычно 7).
2. **Менеджеру по продажам — о ежемесячной оплате.** Каждый день в 09:00 проверяет клиентов с помесячной оплатой. Если до очередной даты оплаты осталось 4 дня (настраивается), отправляет письмо закреплённому менеджеру с копией техническому директору и ИТ и создаёт заявку в ОКДЕСК.

Расписание встроено в саму программу (библиотека `schedule`), отдельные таймеры systemd не нужны.

---

## Содержание

- [Как это работает](#как-это-работает)
  - [Оповещение об окончании подписки](#1-оповещение-об-окончании-подписки-0700)
  - [Ежемесячное напоминание менеджеру об оплате](#2-ежемесячное-напоминание-менеджеру-об-оплате-0900)
  - [Схема](#схема)
- [Где включается напоминание об оплате](#где-включается-напоминание-об-оплате)
- [Структура проекта](#структура-проекта)
- [База данных](#база-данных)
- [Настройка (.env)](#настройка-env)
- [Установка](#установка)
- [Запуск](#запуск)
- [Ручной запуск и проверка напоминаний](#ручной-запуск-и-проверка-напоминаний)
- [Тесты](#тесты)
- [Логи](#логи)
- [ОКДЕСК](#окдеск)
- [Частые вопросы и неполадки](#частые-вопросы-и-неполадки)
- [Полезные SQL-запросы](#полезные-sql-запросы)
- [Репозитории и выкладка](#репозитории-и-выкладка)
- [Связанные программы](#связанные-программы)

---

## Как это работает

### 1. Оповещение об окончании подписки (07:00)

Файлы: `main.py` (`job`), `crud.py` (`get_all_subs_from_time`), `okdesk_handler.py` (`create_iss_okdesk`).

1. Берутся активные подписки (`subscription_start <= сейчас <= subscription_end`), у которых до окончания осталось ровно `subs_day_send` дней. Считается так: `DATEDIFF(subscription_end, сейчас) = subs_day_send`.
2. Клиент определяется через `Login_users`: совпадение логина, пароля и системы мониторинга подписки, затем `Login_users.contragent_id` → `Contragents`.
3. Подписки группируются по клиенту (`Contragents.ok_desk_id`). Клиенты без `ok_desk_id` пропускаются, в лог пишется предупреждение.
4. На каждого клиента создаётся **одна** заявка в ОКДЕСК:
   - тип `subs_stop_services`;
   - компания — `Contragents.ok_desk_id`;
   - ответственный — сотрудник ОКДЕСК с id `2`;
   - срок — через 14 дней;
   - заголовок: «Внимание! Окончание подписки на сервисы через N дня/дней (Клиент)»;
   - описание: HTML-таблица объектов клиента с тарифом Premium или VIP (`stealth_type` 0 или 1).

> Оповещение срабатывает только в тот день, когда до конца подписки осталось ровно `subs_day_send` дней. Если программа в этот день не работала, оповещение по этой подписке не придёт.

### 2. Ежемесячное напоминание менеджеру об оплате (09:00)

Файлы: `pay_remind.py`, `pay_remind_crud.py`, `mailer.py`.

Задача: некоторые клиенты берут подписку на несколько месяцев (например, тариф `VIP-8-6` на 6 месяцев), но платят помесячно. Менеджеру нужно вовремя заключить с клиентом договор на следующий месяц.

**Какие подписки участвуют.** Те, у которых в `info_serv_obj` заполнено `pay_remind_days`, то есть галочка включена в биллинге, и которые действуют на текущий день.

**Даты оплаты.** Это то же число, что и начало подписки, в каждом следующем месяце. Напоминание приходит за `pay_remind_days` дней (по умолчанию 4) до даты оплаты.

| Начало подписки | Окончание | Даты оплаты | Напоминания (за 4 дня) |
|---|---|---|---|
| 15.09.2026 | 15.03.2027 | 15.10, 15.11, 15.12, 15.01, 15.02 | 11.10, 11.11, 11.12, 11.01, 11.02 |
| 31.01.2027 | 31.07.2027 | 28.02, 31.03, 30.04, 31.05, 30.06 | 24.02, 27.03, 26.04, 27.05, 26.06 |

Правила:

- **Короткие месяцы.** Если такого числа в месяце нет (31-е в феврале), дата оплаты сдвигается на последний день месяца.
- **Последний месяц.** Дата, в которую подписка заканчивается, не считается: платить дальше не за что, напоминания не будет.
- **Окно отправки.** Напоминание отправляется с «дата оплаты − N дней» по саму дату оплаты включительно. Если в день напоминания программа не работала или не сработала почта или ОКДЕСК, недостающее дошлётся в следующие дни этого окна.
- **Без повторов.** Что уже отправлено, записывается в таблицу `info_serv_pay_remind_log`: одна строка на клиента и дату оплаты. Письмо и заявка отмечаются отдельно, поэтому повтор отправит только то, что не прошло.
- **Одно письмо на клиента.** Если у клиента несколько подписок с напоминанием и одинаковой датой оплаты, уходит одно письмо, где они перечислены таблицей.

**Кому уходит.**

| Канал | Получатель |
|---|---|
| Письмо, «Кому» | менеджер подписки (`pay_remind_manager_id` → `auth_user.email`) |
| Письмо, «Копия» | адреса из `PAY_REMIND_CC` (по умолчанию технический директор и ИТ) |
| Заявка ОКДЕСК | компания клиента (`Contragents.ok_desk_id`), ответственный — сотрудник ОКДЕСК с той же почтой, что у менеджера; если такого нет — `PAY_REMIND_OK_ASSIGNEE` |

Если менеджер не указан или у него нет почты, письмо уходит только на адреса из `PAY_REMIND_CC`, а в тексте написано «менеджер не указан».

**Письмо.**

- Тема: `Договор на сервисы: <Клиент> — оплата с <ДД.ММ.ГГГГ>`.
- Внутри:
  - дата оплаты;
  - таблица подписок: тариф, число ТС, срок подписки, следующий оплачиваемый месяц;
  - менеджер;
  - список ТС.
- Тот же HTML идёт в описание заявки ОКДЕСК. Заголовок заявки: `Заключить договор на сервисы с <дата> (<Клиент>)`, срок — дата оплаты, 17:30.

### Схема

```
                 billing_web (/services_management, /serv_contragents)
                         │  галочка «Напоминать об оплате»
                         ▼
 ┌──────────────────────────── MySQL suntel ─────────────────────────────┐
 │ info_serv_obj  (subs_day_send, pay_remind_days, pay_remind_manager_id)│
 │ Login_users → Contragents (ok_desk_id, ca_name)    ca_objects         │
 │ info_serv_tarifs   auth_user (менеджеры, почта)                        │
 │ info_serv_pay_remind_log  (что уже отправлено)                         │
 └───────────────────────────────────────────────────────────────────────┘
                         ▲  чтение / журнал
                         │
          check_information_services_subscription (main.py)
            │                                   │
   07:00  job()                         09:00  pay_remind.job()
   окончание подписки                   ежемесячная оплата
            │                                   │
            ▼                                   ├──► SMTP: письмо менеджеру + копии
   ОКДЕСК: заявка subs_stop_services            └──► ОКДЕСК: заявка pay_remind
```

---

## Где включается напоминание об оплате

Напоминание настраивается в **billing_web**, сама программа только читает настройки.

- **Новая подписка** (`/services_management`): галочка «Напоминать менеджеру об оплате каждый месяц», число дней (по умолчанию 4) и менеджер. Менеджер подставляется сам, если основной менеджер клиента из 1С (`Contragents.key_manager`) есть среди пользователей биллинга.
- **Существующая подписка** (`/serv_contragents`): колонка «Оплата помесячно» с кнопкой у каждой подписки. Кнопка открывает окно, где напоминание включается или выключается, задаются дни и менеджер. Там же видна ближайшая дата оплаты и день напоминания.

Без биллинга то же самое можно сделать SQL-запросом, см. [Полезные SQL-запросы](#полезные-sql-запросы).

---

## Структура проекта

| Файл | Что делает |
|---|---|
| `main.py` | Точка входа: планировщик (07:00 и `PAY_REMIND_AT`), задача оповещения об окончании подписок, ручной запуск `python main.py pay_remind …` |
| `config.py` | Настройки из `.env` |
| `crud.py` | Запрос подписок для оповещения об окончании |
| `okdesk_handler.py` | Текст и создание заявки об окончании подписки |
| `okdesc_class.py` | Клиент API ОКДЕСК: создание заявок (`create_issues`, необязательный `deadline_at`), список сотрудников (`get_all_employ`) |
| `pay_remind.py` | Ежемесячные напоминания: расчёт дат оплаты, сборка писем, отправка, журнал |
| `pay_remind_crud.py` | SQL для напоминаний: подписки с включённым напоминанием, журнал `info_serv_pay_remind_log` |
| `mailer.py` | Отправка HTML-письма через SMTP (STARTTLS) |
| `db_conectors.py` | Подключение к MySQL с TLS (`certs/root.crt`) |
| `mysql_models.py` | Модели SQLAlchemy базы `suntel` (сгенерированы sqlacodegen) |
| `my_logger.py` | Логгер, пишет в `log.txt` |
| `certs/root.crt` | Корневой сертификат для TLS-подключения к MySQL |
| `tests/test_pay_remind.py` | Тесты напоминаний, без базы, почты и ОКДЕСК |
| `requirements.txt` | Зависимости |

---

## База данных

База `suntel` (MySQL 8), подключение с TLS.

**Что программа читает:**

| Таблица | Зачем |
|---|---|
| `info_serv_obj` | Подписки: даты, `subs_day_send`, `stealth_type`, `pay_remind_days`, `pay_remind_manager_id`, `info_serv_tarif_id` |
| `Login_users` | Связь подписки с клиентом по логину, паролю и системе мониторинга |
| `Contragents` | Название клиента, `ok_desk_id` |
| `ca_objects` | Название объекта (ТС) |
| `info_serv_tarifs` | Название тарифа |
| `auth_user` | ФИО и почта менеджера |

**Что программа пишет:** только `info_serv_pay_remind_log`.

### Миграция для напоминаний об оплате

Выполнить один раз (например, в DBeaver), **до** выкладки новой версии billing_web:

```sql
-- 1. Две колонки у подписок
ALTER TABLE suntel.info_serv_obj
  ADD COLUMN pay_remind_days TINYINT NULL DEFAULT NULL
      COMMENT 'За сколько дней до очередной даты оплаты (число начала подписки каждый месяц) напоминать менеджеру. NULL - не напоминать',
  ADD COLUMN pay_remind_manager_id INT NULL DEFAULT NULL
      COMMENT 'Кому напоминать: auth_user.id менеджера по продажам',
  ALGORITHM=INSTANT;

-- 2. Связь менеджера с пользователями биллинга
ALTER TABLE suntel.info_serv_obj
  ADD CONSTRAINT pay_remind_manager_FK FOREIGN KEY (pay_remind_manager_id)
      REFERENCES suntel.auth_user (id) ON DELETE SET NULL ON UPDATE RESTRICT;

-- 3. Журнал: какому клиенту о какой дате оплаты уже напомнили
CREATE TABLE suntel.info_serv_pay_remind_log (
  id INT NOT NULL AUTO_INCREMENT,
  contragent_id INT NOT NULL COMMENT 'Клиент (Contragents.ca_id)',
  pay_date DATE NOT NULL COMMENT 'Дата очередной оплаты, о которой напомнили (число начала подписки)',
  mail_to VARCHAR(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL COMMENT 'Кому ушло письмо',
  mail_sent_at DATETIME DEFAULT NULL COMMENT 'Когда ушло письмо. NULL - ещё не ушло',
  okdesk_issue_id INT DEFAULT NULL COMMENT 'Номер заявки в ОКДЕСК. NULL - ещё не создана',
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY pay_remind_client_date_UQ (contragent_id, pay_date),
  CONSTRAINT pay_remind_client_FK FOREIGN KEY (contragent_id) REFERENCES suntel.Contragents (ca_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci COMMENT='Напоминания менеджерам об оплате сервисов';
```

Если у пользователя БД из `.env` нет прав на запись, выдайте их на журнал:

```sql
GRANT SELECT, INSERT, UPDATE ON suntel.info_serv_pay_remind_log TO 'пользователь'@'%';
```

---

## Настройка (.env)

Файл `.env` лежит в корне проекта и в git не попадает (он есть в `.gitignore`).

| Переменная | По умолчанию | Описание |
|---|---|---|
| `OK_URL` | — | Адрес API ОКДЕСК, со слешем в конце: `https://<домен>.okdesk.ru/api/` |
| `OK_TOKEN` | — | Токен API ОКДЕСК |
| `DB_HOST` | — | Хост MySQL |
| `MYSQL_PORT` | — | Порт MySQL |
| `MYSQL_DB_NAME` | — | База, обычно `suntel` |
| `MYSQL_USER` | — | Пользователь MySQL |
| `MYSQL_PASSWORD` | — | Пароль MySQL |
| `SMTP_SERVER` | — | SMTP-сервер, можно с портом: `smtp.yandex.ru:587` |
| `EMAIL_SENDER` | — | Ящик-отправитель, например `noreply@…` |
| `EMAIL_PASSWORD` | — | Пароль ящика. Для Яндекса — **пароль приложения** |
| `PAY_REMIND_CC` | `v.golovanov@suntel-nn.ru,m.stepanenkov@suntel-nn.ru` | Кому всегда ставить копию, через запятую |
| `PAY_REMIND_AT` | `09:00` | Во сколько каждый день проверять напоминания |
| `PAY_REMIND_OK_TYPE` | `pay_remind` | Код типа заявки ОКДЕСК для напоминаний. Пусто — заявки не создавать, только письма |
| `PAY_REMIND_OK_ASSIGNEE` | `2` | Ответственный в ОКДЕСК, если менеджера не нашли среди сотрудников по почте |
| `PAY_REMIND_TEST_TO` | пусто | Тестовый режим: все письма только на этот адрес, без копий, без ОКДЕСК, без журнала. В работе должно быть пусто |

Пример (значения — заглушки):

```dotenv
OK_URL=https://example.okdesk.ru/api/
OK_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx

DB_HOST=192.168.0.10
MYSQL_PORT=3306
MYSQL_DB_NAME=suntel
MYSQL_USER=user
MYSQL_PASSWORD=password

SMTP_SERVER=smtp.yandex.ru:587
EMAIL_SENDER=noreply@example.ru
EMAIL_PASSWORD=app-password
PAY_REMIND_CC=v.golovanov@suntel-nn.ru,m.stepanenkov@suntel-nn.ru
PAY_REMIND_AT=09:00
PAY_REMIND_OK_TYPE=pay_remind
PAY_REMIND_OK_ASSIGNEE=2
PAY_REMIND_TEST_TO=
```

> Отправка идёт через STARTTLS, поэтому для Яндекса укажите порт явно: `smtp.yandex.ru:587`. Без порта программа пойдёт на 25-й, который с сервера часто закрыт.

---

## Установка

Нужен Python 3.10 или новее (проверено на 3.10 и 3.13).

```bash
git clone https://github.com/Jagernau/check_information_services_subscription.git
cd check_information_services_subscription

python3 -m venv env
. env/bin/activate
pip install -r requirements.txt

cp /путь/к/.env .env    # или создать по примеру выше
```

`certs/root.crt` уже лежит в репозитории. Путь к нему относительный, поэтому программу всегда запускайте **из папки проекта**. Туда же пишется `log.txt`.

---

## Запуск

```bash
python main.py
```

Программа работает постоянно. Раз в 30 секунд она проверяет, не пора ли выполнить задачу:

| Время | Задача |
|---|---|
| 07:00 | Оповещение клиентов об окончании подписки |
| `PAY_REMIND_AT` (09:00) | Ежемесячные напоминания менеджерам об оплате |

Время берётся по часам сервера, поэтому на сервере должен стоять часовой пояс Europe/Moscow.

### systemd

Служба называется по имени папки: `check_information_services_subscription.service`.

```ini
# /etc/systemd/system/check_information_services_subscription.service
[Unit]
Description=check_information_services_subscription — оповещения по подпискам на сервисы
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=<пользователь>
WorkingDirectory=/home/<пользователь>/check_information_services_subscription
ExecStart=/home/<пользователь>/check_information_services_subscription/env/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now check_information_services_subscription.service
sudo systemctl status check_information_services_subscription.service
sudo systemctl restart check_information_services_subscription.service   # после обновления кода или .env
```

После перезапуска в `log.txt` должны появиться строки:

```
Запуск планировщика. Задача запланирована ежедневно в 07:00.
Напоминания менеджерам об оплате — ежедневно в 09:00.
```

---

## Ручной запуск и проверка напоминаний

Ручной запуск не трогает работающую службу: он выполняет одну проверку и завершается. Дату можно подставить любую, будто «сегодня» — это она.

```bash
python main.py pay_remind                      # как плановый запуск сегодня
python main.py pay_remind 2026-11-11 --dry     # только показать, что ушло бы 11.11.2026
python main.py pay_remind 2026-11-11 --test    # отправить без менеджера (см. таблицу)
```

| Режим | Письмо | Копии | Заявка ОКДЕСК | Журнал |
|---|---|---|---|---|
| `--dry` | не отправляется, только вывод на экран | — | нет | не трогается |
| `--test` | на адреса `PAY_REMIND_CC`, тема и плашка «[ТЕСТ]», менеджеру не уходит | — | да, с пометкой «[ТЕСТ]», ответственный `PAY_REMIND_OK_ASSIGNEE` | не трогается |
| `PAY_REMIND_TEST_TO` в `.env` | только на этот адрес, «[ТЕСТ]» в теме | нет | нет | не трогается |
| без флагов | менеджеру | `PAY_REMIND_CC` | да, ответственный — менеджер | записывается |

> ⚠️ Запуск с датой **без** `--dry` и `--test` отправляет настоящее письмо менеджеру и создаёт настоящую заявку. Отметка попадает в журнал, и в настоящий день напоминание уже не повторится.

Тестовая заявка (`--test`) создаётся на реальную компанию клиента в ОКДЕСК, после проверки её нужно закрыть.

Пример вывода `--dry`:

```
11.11.2026 — к отправке 1 (проверка, ничего не отправляется)
<Клиент>, оплата с 15.11.2026: письмо → manager@… (копия v.golovanov@…, m.stepanenkov@…); заявка в ОКДЕСК на компанию <ok_desk_id>
```

Порядок проверки после изменений:

1. `python -m pytest -q` — все тесты зелёные.
2. `python main.py pay_remind <дата напоминания> --dry` — в списке те клиенты и получатели, что нужно.
3. `python main.py pay_remind <дата напоминания> --test` — письмо пришло вам и техдиректору, тестовая заявка создалась. Заявку закрыть.
4. Перезапустить службу.

---

## Тесты

```bash
pip install pytest
python -m pytest -q
```

Тесты не ходят в базу, на почту и в ОКДЕСК, всё подменено. Проверяется:

- расчёт дат оплаты: каждое 11-е для подписки с 15-го, сдвиг для 31-го числа, конец подписки, окно до даты оплаты включительно;
- сборка напоминаний: группировка объектов подписки, дубли строк подписок;
- письмо: экранирование названий, «менеджер не указан»;
- отправка: одно письмо и одна заявка, повтор на следующий день ничего не дублирует, письмо дошлётся, если в первый день не ушло;
- режимы `--dry`, `--test` и `PAY_REMIND_TEST_TO` ничего не пишут в журнал; после `--test` настоящая отправка уходит менеджеру.

Предупреждение `MovedIn20Warning … declarative_base()` из `db_conectors.py` на работу не влияет.

---

## Логи

Всё пишется в `log.txt` в папке проекта (в git не попадает). В журнал systemd попадают только ошибки запуска Python.

Строки напоминаний начинаются с `Напоминания об оплате:`

```
Напоминания об оплате: 11.11.2026 — к отправке 1
Напоминания об оплате: <Клиент>, оплата с 15.11.2026: письмо → manager@…, v.golovanov@…, m.stepanenkov@…
Напоминания об оплате: <Клиент>, оплата с 15.11.2026: заявка ОКДЕСК 123456, ответственный 31
Напоминания об оплате: <Клиент>, оплата с 15.11.2026: письмо не ушло, повторю завтра: <ошибка>
```

Полезные команды:

```bash
tail -f log.txt                                   # смотреть в реальном времени
grep "Напоминания об оплате" log.txt | tail -50   # последние напоминания
grep -E "ERROR|не ушло|не создана" log.txt | tail # ошибки
```

---

## ОКДЕСК

| Тип заявки | Откуда | Кому |
|---|---|---|
| `subs_stop_services` | окончание подписки (07:00) | компания клиента, ответственный id `2`, срок +14 дней |
| `pay_remind` (`PAY_REMIND_OK_TYPE`) | ежемесячное напоминание (09:00) | компания клиента, ответственный — менеджер (по почте), срок — дата оплаты 17:30 |

- Тип `pay_remind` нужно завести в ОКДЕСК заранее, иначе заявка не создастся. В логе будет ошибка, письма уйдут, а заявку программа будет пытаться создать каждый день до даты оплаты.
- Заявка о напоминании висит на компании клиента. Проверьте в настройках типа, что клиент не видит её в личном кабинете.
- Менеджера ищем среди сотрудников ОКДЕСК по совпадению почты (`auth_user.email` = почта сотрудника ОКДЕСК, без учёта регистра).
- Обе заявки отправляют `custom_parameters`: `ts_quantity=1` и `labor_intensity=1`.

---

## Частые вопросы и неполадки

**Письмо не ушло.** Смотрите строку `письмо не ушло` в `log.txt`.
- `Connection refused` / timeout — не указан порт 587 или сервер не пускает наружу.
- `Authentication failed` — для Яндекса нужен пароль приложения, а не пароль ящика.
- Программа повторит отправку на следующий день, до даты оплаты включительно.

**Заявка не создалась.** Строка `ОКДЕСК не создал заявку` — обычно не заведён тип `pay_remind` или неверный `OK_TOKEN`. Строка `у клиента нет ok_desk_id` — клиенту не проставлен `Contragents.ok_desk_id`.

**Напоминание не пришло, хотя должно.**
1. У подписки заполнено `pay_remind_days`? (SQL ниже.)
2. Подписка действует сегодня и не заканчивается в эту же дату оплаты?
3. Сегодня входит в окно «дата оплаты − N дней … дата оплаты»?
4. Нет ли уже строки в `info_serv_pay_remind_log` по этому клиенту и дате? Если есть, напоминание уже ушло.
5. Проверьте `python main.py pay_remind <дата> --dry`.

**Нужно отправить напоминание ещё раз.** Удалите строку журнала (SQL ниже) и запустите `python main.py pay_remind`. Можно дождаться и планового запуска, если дата оплаты ещё не прошла.

**Нужно только письмо, без ОКДЕСК.** В `.env` поставьте `PAY_REMIND_OK_TYPE=` и перезапустите службу.

**Менеджер не подставился в биллинге.** Основной менеджер клиента из 1С (`Contragents.key_manager`) ищется среди активных пользователей биллинга по «Фамилия Имя». Если у сотрудника нет учётки, она неактивна или имя и фамилия в ней перепутаны, выберите менеджера вручную.

**Сдвинуть время проверки.** `PAY_REMIND_AT=10:00` в `.env`, затем перезапуск службы.

---

## Полезные SQL-запросы

Какие подписки напоминают и кому:

```sql
SELECT c.ca_id, c.ca_name, t.name AS tarif,
       o.subscription_start, o.subscription_end,
       o.pay_remind_days, CONCAT_WS(' ', u.last_name, u.first_name) AS manager, u.email,
       COUNT(DISTINCT o.serv_obj_sys_mon_id) AS ts, COUNT(*) AS subs
FROM suntel.info_serv_obj o
JOIN suntel.Login_users l ON l.login = o.sys_login AND l.password = o.sys_password AND l.system_id = o.monitoring_sys
JOIN suntel.Contragents c ON c.ca_id = l.contragent_id
LEFT JOIN suntel.info_serv_tarifs t ON t.tarif_id = o.info_serv_tarif_id
LEFT JOIN suntel.auth_user u ON u.id = o.pay_remind_manager_id
WHERE o.pay_remind_days IS NOT NULL AND o.subscription_end >= NOW()
GROUP BY c.ca_id, c.ca_name, t.name, o.subscription_start, o.subscription_end,
         o.pay_remind_days, u.last_name, u.first_name, u.email;
```

Включить напоминание клиенту (за 4 дня, менеджер по логину биллинга):

```sql
UPDATE suntel.info_serv_obj o
JOIN suntel.Login_users l
  ON o.sys_login = l.login AND o.sys_password = l.password AND o.monitoring_sys = l.system_id
SET o.pay_remind_days = 4,
    o.pay_remind_manager_id = (SELECT id FROM suntel.auth_user WHERE username = '<логин менеджера>')
WHERE l.contragent_id = <ca_id клиента>
  AND o.subscription_end > NOW();
```

Выключить напоминание клиенту:

```sql
UPDATE suntel.info_serv_obj o
JOIN suntel.Login_users l
  ON o.sys_login = l.login AND o.sys_password = l.password AND o.monitoring_sys = l.system_id
SET o.pay_remind_days = NULL, o.pay_remind_manager_id = NULL
WHERE l.contragent_id = <ca_id клиента>;
```

Что уже отправлено:

```sql
SELECT g.pay_date, c.ca_name, g.mail_to, g.mail_sent_at, g.okdesk_issue_id, g.created_at
FROM suntel.info_serv_pay_remind_log g
JOIN suntel.Contragents c ON c.ca_id = g.contragent_id
ORDER BY g.pay_date DESC, c.ca_name;
```

Отправить напоминание повторно:

```sql
-- всё заново (письмо и заявку)
DELETE FROM suntel.info_serv_pay_remind_log
WHERE contragent_id = <ca_id клиента> AND pay_date = '<ГГГГ-ММ-ДД>';

-- только письмо
UPDATE suntel.info_serv_pay_remind_log SET mail_sent_at = NULL
WHERE contragent_id = <ca_id клиента> AND pay_date = '<ГГГГ-ММ-ДД>';
```

---

## Репозитории и выкладка

Код хранится в двух местах:

- GitHub: `https://github.com/Jagernau/check_information_services_subscription`
- SourceCraft: `ssh://ssh.sourcecraft.dev/api-suntel-suntel-nn-ru/check-information-services-subscription.git`

Чтобы один `git push` отправлял в оба, а `git pull` брал из GitHub (настраивается один раз в каждой копии репозитория):

```bash
git remote set-url --add --push origin https://github.com/Jagernau/check_information_services_subscription.git
git remote set-url --add --push origin ssh://ssh.sourcecraft.dev/api-suntel-suntel-nn-ru/check-information-services-subscription.git
git remote -v
# origin  https://github.com/Jagernau/check_information_services_subscription.git (fetch)
# origin  https://github.com/Jagernau/check_information_services_subscription.git (push)
# origin  ssh://ssh.sourcecraft.dev/api-suntel-suntel-nn-ru/check-information-services-subscription.git (push)
```

Обновление на сервере:

```bash
cd ~/check_information_services_subscription
git pull
. env/bin/activate && pip install -r requirements.txt   # если менялись зависимости
python -m pytest -q
sudo systemctl restart check_information_services_subscription.service
grep "Запуск планировщика\|Напоминания менеджерам" log.txt | tail -2
```

Если в версии есть изменения базы, сначала выполните SQL, затем выкладывайте программу и billing_web.

---

## Связанные программы

| Программа | Связь |
|---|---|
| **billing_web** | Создание подписок и настройка напоминаний (`app/pay_remind.py`, страницы `/services_management` и `/serv_contragents`) |
| **information_services_backend** (ядро) | Строит отчёты по тем же подпискам `info_serv_obj`. С этой программой напрямую не связано |
| **information_services_send** | Отправляет отчёты клиентам. Своя логика заморозок и эскалаций менеджерам, не пересекается |
| **mail_sender** | Рассылки клиентам. Те же настройки SMTP можно взять оттуда |
