from okdesc_class import OkdeskClass
from config import OK_TOKEN, OK_URL
from my_logger import logger

def create_iss_okdesk(client_okdesk_id, company_name, objects_list, days_left):
    """
    Создает заявку в Okdesk с HTML-перечнем истекающих объектов.
    days_left - количество дней до окончания подписки.
    """
    try:
        ok_class = OkdeskClass(OK_URL, OK_TOKEN)

        service_types = {
            0: '<span style="background-color: #e8f0fe; color: #1a73e8; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">Premium</span>',
            1: '<span style="background-color: #fce8e6; color: #d93025; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">VIP</span>'
        }

        table_rows = []
        for obj in objects_list:
            serv_badge = service_types.get(obj['type'], '<span style="color: #666;">Неизвестно</span>')
            table_rows.append(f"""
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; color: #333333; font-size: 14px;">{obj['name']}</td>
                    <td style="padding: 10px; text-align: center;">{serv_badge}</td>
                </tr>
            """)
        rows_html = "".join(table_rows)

        # Используем переданное количество дней
        text_title = f"Внимание! Окончание подписки на сервисы через {days_left} дня/дней ({company_name})"
        text_descr = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 650px; line-height: 1.6; color: #202124;">
            <p style="font-size: 15px; margin-bottom: 16px;">Уважаемый клиент!</p>
            <p style="font-size: 14px; margin-bottom: 20px;">
                Уведомляем вас о том, что <strong>через {days_left} дня/дней</strong> истекает срок действия подписки на сервисы для следующих объектов:
            </p>
            <table style="width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; margin-bottom: 24px;">
                <thead>
                    <tr style="background-color: #f8f9fa; border-bottom: 2px solid #e0e0e0;">
                        <th style="padding: 12px 10px; text-align: left; color: #5f6368; font-weight: 600; font-size: 13px;">Наименование объекта</th>
                        <th style="padding: 12px 10px; text-align: center; color: #5f6368; font-weight: 600; font-size: 13px; width: 120px;">Тариф</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div style="background-color: #fef7e0; border-left: 4px solid #f4b400; color: #b06000; padding: 12px 16px; border-radius: 0 4px 4px 0; font-size: 13.5px;">
                <strong>Важно:</strong> Пожалуйста, позаботьтесь о своевременном продлении, чтобы избежать автоматической приостановки сервисов.
            </div>
        </div>
        """

        ok_class.create_issues(
            title=text_title,
            description=text_descr,
            company_id=str(client_okdesk_id),
            assignee_id=str(2),
            maintenance_entity_id=None,
            type_iss="subs_stop_services"
        )
        logger.info(f'Успешно создана HTML-заявка для компании {company_name} (ID: {client_okdesk_id})')
    except Exception as e:
        logger.error(f'Не удалось создать HTML-заявку для {client_okdesk_id}, ошибка: {e}')
