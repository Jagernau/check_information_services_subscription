from os import environ as envi
from dotenv import load_dotenv

load_dotenv()

OK_URL = envi.get('OK_URL')
OK_TOKEN = envi.get('OK_TOKEN')

DB_HOST=envi.get('DB_HOST')
MYSQL_USER=envi.get('MYSQL_USER')
MYSQL_DB_NAME=envi.get('MYSQL_DB_NAME')
MYSQL_PASSWORD=envi.get('MYSQL_PASSWORD')
MYSQL_PORT=envi.get('MYSQL_PORT')
connection_mysql = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}"

# ============================================================================
# Ежемесячные напоминания менеджерам об оплате сервисов
# ============================================================================
#: Почта, с которой уходят напоминания (те же настройки, что в mail_sender)
SMTP_SERVER = envi.get('SMTP_SERVER', '')
EMAIL_SENDER = envi.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = envi.get('EMAIL_PASSWORD', '')
#: Кому всегда ставить копию, через запятую
PAY_REMIND_CC = [a.strip() for a in envi.get(
    'PAY_REMIND_CC', 'v.golovanov@suntel-nn.ru,m.stepanenkov@suntel-nn.ru').split(',') if a.strip()]
#: Во сколько каждый день проверять, кому пора напомнить
PAY_REMIND_AT = envi.get('PAY_REMIND_AT', '09:00')
#: Код типа заявки в ОКДЕСК для напоминаний. Пусто — заявки не создавать, только почта
PAY_REMIND_OK_TYPE = envi.get('PAY_REMIND_OK_TYPE', 'pay_remind')
#: Ответственный в ОКДЕСК, если менеджера не нашли среди сотрудников по почте
PAY_REMIND_OK_ASSIGNEE = envi.get('PAY_REMIND_OK_ASSIGNEE', '2')
#: Тестовый режим: если задан адрес, все письма уходят только на него, без копий,
#: заявки в ОКДЕСК не создаются и в журнал ничего не пишется
PAY_REMIND_TEST_TO = envi.get('PAY_REMIND_TEST_TO', '').strip()
