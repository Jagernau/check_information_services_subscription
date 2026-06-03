import time
import random
import requests
import sys
from datetime import datetime, timedelta, date
sys.path.append('../')
from my_logger import logger

class OkdeskClass:
    def __init__(self, ok_url: str, ok_token: str,) -> None:
        """
        Initializes the OkdescSender object.

        Args:
            ok_url (str): okdesc address.
            ok_token (str): okdesc token.
        """
        self.ok_url = ok_url
        self.ok_token = ok_token

    def __get_request(self, url):
        """Универсальный метод для выполнения GET-запросов"""
        time.sleep(random.uniform(1.2, 1.7))
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"Не получен GET")
                return None
        
    def create_issues(self, 
                    title: str, # Название заявки
                    description: str, # Описание заявки
                    company_id: str, # ИД компании
                    #contact_id: str, #
                    assignee_id: str, # ИД ответственного за компанию
                    maintenance_entity_id: str, # ИД объекта 
                    type_iss: str, # Код типа заявки
                    #priority: str, # Код приоритета заявки
                    #default_assignee_id,
                ):
        time.sleep(random.uniform(1.2, 1.7))
        url = f"{self.ok_url}v1/issues/?api_token={self.ok_token}"
        
        data = {
                "title": title, # Название заявки
                "description": description, # Описание заявки
                "company_id": company_id, # ИД компании
                "deadline_at": str(date.today() + timedelta(days=14)) + " 17:30",
                #"contact_id": contact_id, #
                "assignee_id": str(assignee_id), # ИД ответственного за компанию
                "maintenance_entity_id": maintenance_entity_id, # ИД объекта 
                "type": str(type_iss), # Код типа заявки
                #"priority": priority, # Код приоритета заявки
                #"default_assignee_id": default_assignee_id,
                "custom_parameters": {"ts_quantity": "1", "labor_intensity": "1"}
                }
        response = requests.post(url, json=data)
        
        # Обработка ответа
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Не сохранились данные {response.status_code} {response.text} {data}")


    def get_all_employ(self):
        """
        Метод получения всех сотрудников
        """
        return self.__get_request(f"{self.ok_url}v1/employees/list?api_token={self.ok_token}")


    def change_status_issues(self,
                ok_issues_id
                ):
        time.sleep(random.uniform(1.2, 1.7))
        url = f"{self.ok_url}v1/issues/{ok_issues_id}/statuses?api_token={self.ok_token}"
        
        data = {
                "code": "complete_ai",
                "comment": "Заявка создана автоматически с помощью робота"
                }
        response = requests.post(url, json=data)
        
        # Обработка ответа
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Не сохранились данные {response.status_code} {response.text} {data}")

