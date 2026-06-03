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

