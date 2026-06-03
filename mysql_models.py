
from typing import List, Optional

from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, Table, Text, Time, text
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT, SMALLINT, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class CellOperator(Base):
    __tablename__ = 'Cell_operator'
    __table_args__ = {'comment': 'Таблица для хранения информации об операторах сотовой связи'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(60), comment='Имя сотового оператора')
    ca_price: Mapped[Optional[int]] = mapped_column(Integer, comment='цена для клиентов')
    sun_price: Mapped[Optional[int]] = mapped_column(Integer, comment='Цена для Сантел')

    sim_cards: Mapped[List['SimCards']] = relationship('SimCards', back_populates='Cell_operator')


t_GOS_DUBLI = Table(
    'GOS_DUBLI', Base.metadata,
    Column('gov_number', String(70)),
    Column('duplicate_count', BigInteger, server_default=text("'0'"))
)


t_ICCID_меньше_19 = Table(
    'ICCID меньше 19', Base.metadata,
    Column('sim_iccid', String(40))
)


t_OKDESK_CONTACTS = Table(
    'OKDESK_CONTACTS', Base.metadata,
    Column('change_time', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')),
    Column('ca_name', String(255)),
    Column('name', String(50)),
    Column('email', String(80))
)


class PPDKLogging(Base):
    __tablename__ = 'PPDK_logging'

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Лог')
    column_name: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Название колонки')
    change_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Дата изменения')
    old_val: Mapped[Optional[str]] = mapped_column(String(700, 'utf8mb3_unicode_ci'), comment='Старое значение')
    new_val: Mapped[Optional[str]] = mapped_column(String(700, 'utf8mb3_unicode_ci'), comment='Новое значение')
    exist_id: Mapped[Optional[int]] = mapped_column(Integer, comment='OST_order_no')
    type_req: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Тип изменения')


class PPDKTransneft(Base):
    __tablename__ = 'PPDK_transneft'
    __table_args__ = {'comment': 'Заявки по ППДК транснефть'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    OST_order_no: Mapped[int] = mapped_column(Integer, comment='№ заявки в ОСТ\r\n')
    formation_date_app: Mapped[datetime.datetime] = mapped_column(DateTime, comment='"Дата форми-\r\nрования заявки"\r\n')
    OST: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ОСТ\r\n')
    organization: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Организация\r\n')
    type_work: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Вид работ\r\n')
    vehicle_reg_plate: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='"Регистра-\r\nционный знак ТС"\r\n')
    vehic_model: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Марка, модель ТС')
    comment: Mapped[str] = mapped_column(VARCHAR(800), comment='Комментарий\r\n')
    date_first_initial: Mapped[datetime.datetime] = mapped_column(DateTime, comment='"План. дата работ (перво-\r\nначальная предложенная заказчиком)"\r\n')
    plan_date_work: Mapped[datetime.datetime] = mapped_column(DateTime, comment='План. дата работ (оконча-\r\nтельная)')
    vehic_invent_numb: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Инв. № ТС\r\n')
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Тип ТС\r\n')
    fault: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Неисправность\r\n')
    repair_area: Mapped[Optional[str]] = mapped_column(VARCHAR(700), comment='Площадка ремонта\r\n')
    date_transfer_MVDP: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата передачи в МВДП\r\n')
    date_agreement_contrac: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата согласования Исполнителем\r\n')
    processing_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Срок обработки\r\n')
    performer: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Исполнитель\r\n')
    date_centralized: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата и время Централизованной приемки работ\r\n')
    date_acceptance: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата и время приемки работ в ОСТ\r\n')
    dat_accept_works_OST: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Время приемки работ в ОСТ (в формате чч:мм)\r\n')
    status_req: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Статус\r\n')
    dat_closing_app: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата закрытия заявки\r\n')
    comment_primary_doc: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Комментарий, первичный документ из ППДК ОСТ\r\n')
    summary_act: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Сводный акт (в Модуле)\r\n')
    completion_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата завершения работ в ОСТ\r\n')
    days_overdue: Mapped[Optional[int]] = mapped_column(Integer, comment='Кол-во дней просрочки\r\n')


class AdditionalStatuses(Base):
    __tablename__ = 'additional_statuses'
    __table_args__ = (
        Index('add_status_name', 'add_status_name', 'status_code', unique=True),
        Index('status_code', 'status_code'),
        {'comment': 'Таблица дополнительных статусов'}
    )

    id_status: Mapped[int] = mapped_column(Integer, primary_key=True)
    add_status_name: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Имя дополнителя приостановленной причины')
    status_code: Mapped[int] = mapped_column(Integer, comment='Код статуса')
    detail: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Детальное описание')


class AuthGroup(Base):
    __tablename__ = 'auth_group'
    __table_args__ = (
        Index('name', 'name', unique=True),
        {'comment': 'Таблица для хранения групп пользователей ЦМС'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(150), comment='Название группы пользователей ЦМС')

    auth_user_groups: Mapped[List['AuthUserGroups']] = relationship('AuthUserGroups', back_populates='group')
    auth_group_permissions: Mapped[List['AuthGroupPermissions']] = relationship('AuthGroupPermissions', back_populates='group')


class AuthUser(Base):
    __tablename__ = 'auth_user'
    __table_args__ = (
        Index('username', 'username', unique=True),
        {'comment': 'Таблица пользователей ЦМС'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(VARCHAR(128), comment='пароль')
    is_superuser: Mapped[int] = mapped_column(TINYINT(1), comment='принадлежность к суперпользователю')
    username: Mapped[str] = mapped_column(VARCHAR(150), comment='логин')
    first_name: Mapped[str] = mapped_column(VARCHAR(150), comment='имя')
    last_name: Mapped[str] = mapped_column(VARCHAR(150), comment='фамилия')
    email: Mapped[str] = mapped_column(VARCHAR(254), comment='почта')
    is_staff: Mapped[int] = mapped_column(TINYINT(1), comment='является ли сотрудником')
    is_active: Mapped[int] = mapped_column(TINYINT(1), comment='активность аккаунта')
    date_joined: Mapped[datetime.datetime] = mapped_column(DATETIME(fsp=6), comment='дата создания аккаунта')
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DATETIME(fsp=6), comment='последний вход')

    auth_user_groups: Mapped[List['AuthUserGroups']] = relationship('AuthUserGroups', back_populates='user')
    devices_logger_commands: Mapped[List['DevicesLoggerCommands']] = relationship('DevicesLoggerCommands', back_populates='auth_user')
    django_admin_log: Mapped[List['DjangoAdminLog']] = relationship('DjangoAdminLog', back_populates='user')
    auth_user_user_permissions: Mapped[List['AuthUserUserPermissions']] = relationship('AuthUserUserPermissions', back_populates='user')
    devices: Mapped[List['Devices']] = relationship('Devices', back_populates='itprogrammer')
    devices_diagnostics: Mapped[List['DevicesDiagnostics']] = relationship('DevicesDiagnostics', back_populates='programmer')
    service_subscription_log: Mapped[List['ServiceSubscriptionLog']] = relationship('ServiceSubscriptionLog', back_populates='user')
    sim_cards: Mapped[List['SimCards']] = relationship('SimCards', back_populates='itprogrammer')


class DevicesVendor(Base):
    __tablename__ = 'devices_vendor'
    __table_args__ = {'comment': 'Таблица для хранения информации о производителях устройств'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_name: Mapped[Optional[str]] = mapped_column(VARCHAR(35), comment='Название фирмы производителя терминалов')

    devices_brands: Mapped[List['DevicesBrands']] = relationship('DevicesBrands', back_populates='devices_vendor')


class DiscountClient(Base):
    __tablename__ = 'discount_client'
    __table_args__ = {'comment': 'Таблица с вариантами скидок'}

    dis_cl_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID Скидки')
    dis_cl_name: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Название Скидки')
    dis_cl_rate: Mapped[int] = mapped_column(Integer, comment='Процент')

    discount_client_link: Mapped[List['DiscountClientLink']] = relationship('DiscountClientLink', back_populates='dis')


class DiscountObj(Base):
    __tablename__ = 'discount_obj'
    __table_args__ = {'comment': 'Варианты скидок на объекты'}

    dis_obj_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID скидки на объекты')
    dis_obj_name: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Название скидок на объекты')
    dis_obj_rate: Mapped[int] = mapped_column(Integer, comment='Процент скидки на объект')

    discount_obj_link: Mapped[List['DiscountObjLink']] = relationship('DiscountObjLink', back_populates='dis')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model', unique=True),
        {'comment': 'Таблица для хранения типов содержимого Django ЦМС'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_label: Mapped[str] = mapped_column(VARCHAR(100), comment='из какого приложения')
    model: Mapped[str] = mapped_column(VARCHAR(100), comment='из какой модели')

    auth_permission: Mapped[List['AuthPermission']] = relationship('AuthPermission', back_populates='content_type')
    django_admin_log: Mapped[List['DjangoAdminLog']] = relationship('DjangoAdminLog', back_populates='content_type')


class DjangoMigrations(Base):
    __tablename__ = 'django_migrations'
    __table_args__ = {'comment': 'Таблица для хранения информации о миграциях Django ЦМС'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    app: Mapped[str] = mapped_column(VARCHAR(255), comment='таблица')
    name: Mapped[str] = mapped_column(VARCHAR(255), comment='действие')
    applied: Mapped[datetime.datetime] = mapped_column(DATETIME(fsp=6), comment='дата')


class DjangoSession(Base):
    __tablename__ = 'django_session'
    __table_args__ = (
        Index('django_session_expire_date_a5c62663', 'expire_date'),
        {'comment': 'Таблица для хранения сессий Django Заходов в ЦМС'}
    )

    session_key: Mapped[str] = mapped_column(String(40, 'utf8mb3_unicode_ci'), primary_key=True)
    session_data: Mapped[str] = mapped_column(LONGTEXT)
    expire_date: Mapped[datetime.datetime] = mapped_column(DATETIME(fsp=6))


class EmailsSends(Base):
    __tablename__ = 'emails_sends'
    __table_args__ = {'comment': 'Таблица по email рассылкам'}

    send_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sends_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Время отправки')
    email: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Почта')
    send_status: Mapped[int] = mapped_column(TINYINT, comment='Успешность отправки\r\n0 - отправлено\r\n1 - не отправлено')
    confir_status: Mapped[int] = mapped_column(TINYINT, comment='0 - Не подтверждена\r\n1 - Подтверждена')
    mail_header: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Заголовок письма')
    mail_body: Mapped[str] = mapped_column(LONGTEXT, comment='Текст рассылки')
    client_name: Mapped[str] = mapped_column(String(400, 'utf8mb3_unicode_ci'), comment='Имя клиента')
    sender_mail: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Почта рассыльщика')
    user_login: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Логин юзера запустившего рассылку')
    uid_header: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Уникальный ИД темы рассылки')
    sender_params: Mapped[dict] = mapped_column(JSON, comment='Параметры рассылки')
    send_type: Mapped[int] = mapped_column(TINYINT, comment='Через что ведётся рассылка:\r\n0 - почта\r\n1 - ОКДЕСК')
    attachment_path: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb3_unicode_ci'), comment='Место хранения файла')
    comment: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb3_unicode_ci'), comment='Комментарий')


class GlobalLogging(Base):
    __tablename__ = 'global_logging'
    __table_args__ = {'comment': 'Первоначальная Таблица для хранения изменений в таблицах объектов '
                'и клиентов 1с через Python, до тригерного логирования'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_type: Mapped[str] = mapped_column(VARCHAR(50), comment='изменения в объектах или клиентах')
    edit_id: Mapped[int] = mapped_column(Integer, comment='id изменённого')
    field: Mapped[str] = mapped_column(VARCHAR(50), comment='поле изменения')
    old_value: Mapped[Optional[str]] = mapped_column(VARCHAR(8000), comment='старое значение')
    new_value: Mapped[Optional[str]] = mapped_column(VARCHAR(8000), comment='новое значение')
    change_time: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    sys_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Система мониторинга')
    action: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='добавление, изменение или удаление')
    contragent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='логгирование контрагента')


class GuaranteeTerms(Base):
    __tablename__ = 'guarantee_terms'
    __table_args__ = {'comment': 'Таблица для хранения родителей контрагентов'}

    gt_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID гарантийного срока')
    gt_term: Mapped[Optional[int]] = mapped_column(Integer, comment='Срок гарантии (дней)')
    gt_type: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Тип гарантии')


class Holdings(Base):
    __tablename__ = 'holdings'
    __table_args__ = {'comment': 'Таблица для хранения информации о Холдингах по тз'}

    holding_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    holding_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Имя родителя контрагента (Холдинг)')

    Contragents: Mapped[List['Contragents']] = relationship('Contragents', back_populates='ca_holding')


class InfoServTarifClient(Base):
    __tablename__ = 'info_serv_tarif_client'
    __table_args__ = (
        Index('info_serv_client_FK', 'client_id'),
        Index('info_serv_tarifs_FK', 'tarif_id'),
        {'comment': 'Сопоставление ТАРИФ СЕРВИСОВ КЛИЕНТ'}
    )

    tarif_client_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ИД отношений')
    tarif_id: Mapped[int] = mapped_column(Integer, comment='ID Тарифа')
    client_id: Mapped[int] = mapped_column(Integer, comment='ID Клиента')
    start_tarif: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Начало тарифа у клиента')
    end_tarif: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Конец тарифа')


class InfoServTarifs(Base):
    __tablename__ = 'info_serv_tarifs'
    __table_args__ = {'comment': 'Таблица с ТАРИФАМИ СЕРВИСОВ'}

    tarif_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ИД тарифов')
    name: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Название тарифа')
    price: Mapped[int] = mapped_column(Integer, comment='Цена тарифа')
    count: Mapped[Optional[int]] = mapped_column(Integer, comment='Количество доступных сервисов')


class InformationServices(Base):
    __tablename__ = 'information_services'
    __table_args__ = (
        Index('serv_name', 'serv_name', unique=True),
        {'comment': 'Таблица для информационных сервисов Клиентов'}
    )

    serv_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID Сервиса')
    serv_name: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Название сервиса')
    serv_price: Mapped[Optional[int]] = mapped_column(Integer, comment='Цена за сервис')

    info_serv_obj: Mapped[List['InfoServObj']] = relationship('InfoServObj', back_populates='info_obj_serv')


class LogChanges(Base):
    __tablename__ = 'log_changes'
    __table_args__ = {'comment': 'Таблица логирования изменений в данных Базы'}

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    changes_date: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Дата изменения')
    changes_table: Mapped[Optional[str]] = mapped_column(VARCHAR(250), comment='В какой таблице были внесены изменения')
    changes_action: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Название действия:\r\n0 - Del\r\n1 - Insert\r\n2 - Update')
    obj_key: Mapped[Optional[int]] = mapped_column(Integer, comment='Ключ элемента, Практически везде ID. Делаю по ID int')
    changes_column: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Название столбца')
    old_val: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Старое значение')
    new_val: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Новое значение')


class LoginUsersPhones(Base):
    __tablename__ = 'login_users_phones'
    __table_args__ = {'comment': 'Таблица с логинами и паролями и телефонами'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID записи')
    phone: Mapped[str] = mapped_column(String(12, 'utf8mb3_unicode_ci'), comment='телефон')
    login: Mapped[str] = mapped_column(String(12, 'utf8mb3_unicode_ci'), comment='Логин')
    password: Mapped[str] = mapped_column(String(19, 'utf8mb3_unicode_ci'), comment='Пароль')
    mess_name: Mapped[str] = mapped_column(String(40, 'utf8mb3_unicode_ci'), comment='Имя в месседжере')
    mess_user_id: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='ID в меседжере')


class MonitoringSystem(Base):
    __tablename__ = 'monitoring_system'
    __table_args__ = {'comment': 'Таблица для хранения информации о системах мониторинга'}

    mon_sys_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mon_sys_name: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Название системы мониторинга')
    mon_sys_obj_price_suntel: Mapped[Optional[int]] = mapped_column(Integer, comment='Стоимость объекта для Сантел')
    mon_sys_ca_obj_price_default: Mapped[Optional[int]] = mapped_column(Integer, comment='Базовая стоимость объекта для Контрагента')
    mon_url: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Адресс Системы мониторинга')

    inspect_terminals: Mapped[List['InspectTerminals']] = relationship('InspectTerminals', back_populates='monitoring_system_')
    invoicing: Mapped[List['Invoicing']] = relationship('Invoicing', back_populates='system_monitorig')
    Login_users: Mapped[List['LoginUsers']] = relationship('LoginUsers', back_populates='system')
    ca_objects: Mapped[List['CaObjects']] = relationship('CaObjects', back_populates='sys_mon')
    clients_in_system_monitor: Mapped[List['ClientsInSystemMonitor']] = relationship('ClientsInSystemMonitor', back_populates='system_monitor')
    devices: Mapped[List['Devices']] = relationship('Devices', back_populates='sys_mon')
    transfer_client: Mapped[List['TransferClient']] = relationship('TransferClient', foreign_keys='[TransferClient.current_sys_mon]', back_populates='monitoring_system')
    transfer_client_: Mapped[List['TransferClient']] = relationship('TransferClient', foreign_keys='[TransferClient.tranfer_sys_mon_id]', back_populates='tranfer_sys_mon')
    info_serv_obj: Mapped[List['InfoServObj']] = relationship('InfoServObj', back_populates='monitoring_system')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='sys_mon')


class ObjectRetranslators(Base):
    __tablename__ = 'object_retranslators'
    __table_args__ = {'comment': 'Таблица для хранения информации о ретрансляторах'}

    retranslator_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    retrans_protocol: Mapped[int] = mapped_column(TINYINT, comment='Виды протоколов:\r\n1- Egts\r\n2 - Wialon ретранслятор\r\n3- Wialon IPS')
    retranslator_name: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Имя ретранслятора')
    retranslator_suntel_price: Mapped[Optional[int]] = mapped_column(Integer, comment='цена ретрансляции для Сантел')
    retranslator_ca_price: Mapped[Optional[int]] = mapped_column(Integer, comment='Цена ретрансляции для клиента')
    retrans_adres: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Адрес куда ретранслируется')

    group_object_retrans: Mapped[List['GroupObjectRetrans']] = relationship('GroupObjectRetrans', back_populates='retr')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='retrans')


class ObjectStatuses(Base):
    __tablename__ = 'object_statuses'
    __table_args__ = {'comment': 'Таблица для хранения информации о статусах объектов'}

    status_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    abon_bool: Mapped[int] = mapped_column(TINYINT(1), comment='На абонентке или нет')
    status: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Название статуса')

    ca_objects: Mapped[List['CaObjects']] = relationship('CaObjects', back_populates='object_statuses')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='obj_status')


class OkDeskLoggingIss(Base):
    __tablename__ = 'ok_desk_logging_iss'
    __table_args__ = {'comment': 'Логгирование изменение в заявках ОКДЕСК'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_type: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='изменения в объектах или клиентах')
    edit_id: Mapped[Optional[int]] = mapped_column(Integer, comment='id изменённого')
    field: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='поле изменения')
    old_value: Mapped[Optional[dict]] = mapped_column(JSON, comment='старое значение')
    new_value: Mapped[Optional[dict]] = mapped_column(JSON, comment='новое значение')
    change_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время создания заявки')
    action: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='добавление, изменение или удаление\t')


class OnecContacts(Base):
    __tablename__ = 'onec_contacts'
    __table_args__ = {'comment': 'Контакты'}

    contact_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Идентификатор Контактов')
    usesokdesk: Mapped[int] = mapped_column(TINYINT, comment='ИспользуетOKDESK\r\nИспользуется Ли в ОКДЕСК\r\n0-НЕТ\r\n1_ДА')
    connectedtelegram_bot: Mapped[int] = mapped_column(TINYINT, comment='ПодключенКТелеграм_Боту\r\nПодключённ ли к телеграмм\r\n0-нет\r\n1-Да')
    connectedcmob_application: Mapped[int] = mapped_column(TINYINT, comment='ПодключенКМоб_Приложению\r\n0-нет\r\n1-да')
    access_personal_okdesk: Mapped[int] = mapped_column(TINYINT, server_default=text("'0'"), comment='Предоставлен ли доступ клиенту к ОКДЕСК')
    surname: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Фамилия')
    name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Имя')
    patronymic: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Отчество')
    position: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Должность')
    phone: Mapped[Optional[str]] = mapped_column(String(80, 'utf8mb3_unicode_ci'), comment='Телефон')
    mobiletelephone: Mapped[Optional[str]] = mapped_column(String(80, 'utf8mb3_unicode_ci'), comment='МобТелефон')
    email: Mapped[Optional[str]] = mapped_column(String(80, 'utf8mb3_unicode_ci'), comment='ЭлПочта')
    unique_partner_identifier: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторПартнера')
    unique_contact_identifier: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторКонтактногоЛица')
    ok_desk_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ИД в ОК ДЕСК')
    nametelegram: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='ИмяВТелеграм')
    idbmob_application: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='IDВМоб_Приложении')


class OnecContracts(Base):
    __tablename__ = 'onec_contracts'
    __table_args__ = (
        Index('ok_desk_id', 'ok_desk_id', unique=True),
        Index('unique_contract_identifier', 'unique_contract_identifier', unique=True),
        {'comment': 'Таблица с договорами из 1С'}
    )

    contract_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Внутренний ID контракта')
    unique_contract_identifier: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторДоговораКонтрагента')
    name_contract: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='НаименованиеДоговора')
    contract_number: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='НомерДоговора')
    contract_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='ДатаДоговора')
    contract_status: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Статус')
    organization: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Организация')
    partner: Mapped[Optional[str]] = mapped_column(VARCHAR(1000), comment='Партнер')
    counterparty: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb3_unicode_ci'), comment='Контрагент')
    contract_commencement_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='ДатаНачалаДействия')
    contract_expiration_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='ДатаОкончанияДействия')
    contract_purpose: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Цель')
    type_calculations: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ВидРасчетов')
    category: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Категория')
    manager: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Менеджер')
    subdivision: Mapped[Optional[str]] = mapped_column(String(600, 'utf8mb3_unicode_ci'), comment='Подразделение')
    contact_person: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='КонтактноеЛицо')
    organization_bank_account: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='БанковскийСчетОрганизации')
    counterparty_bank_account: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='БанковскийСчетКонтрагента')
    detailed_calculations: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ДетализацияРасчетов')
    unique_partner_identifier: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторПартнера')
    unique_counterparty_identifier: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторКонтрагента')
    ok_desk_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID в ОК-деск')
    signing_status: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='СтатусПодписания')


class OnecOrder(Base):
    __tablename__ = 'onec_order'
    __table_args__ = (
        Index('file_path', 'file_path', unique=True),
        {'comment': 'Таблица заказ нарядов из 1С'}
    )

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_unic_id: Mapped[str] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторАктаТО')
    order_num: Mapped[str] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='ЗаказНарядНомер')
    order_data: Mapped[datetime.datetime] = mapped_column(DateTime, comment='Дата')
    edit_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время создания записи')
    file_path: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ПутьКФайлу')
    obj_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ВнутреннийIDОбъектаБД2')


class ReprogTerms(Base):
    __tablename__ = 'reprog_terms'
    __table_args__ = (
        Index('imei', 'imei', unique=True),
        Index('imei_2', 'imei'),
        {'comment': 'Таблица перепрограммирования терминалов'}
    )

    reprog_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    imei: Mapped[str] = mapped_column(VARCHAR(100), comment='Имей терминала')
    type_term: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='Тип терминала')
    vehicle_name: Mapped[Optional[str]] = mapped_column(VARCHAR(150), comment='Имя объекта')
    client_name: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='Имя клиента')
    comand_name: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Название команды')
    comand: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Команда')
    send_type: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Тип через что была отправка')
    monitoring_system: Mapped[Optional[int]] = mapped_column(Integer, comment='Система мониторинга')
    full_device_name: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Полное название типа терминала')
    data_reprog: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Дата репрог')


class RequestsFromOKDESK(Base):
    __tablename__ = 'requests_from_OKDESK'
    __table_args__ = (
        Index('ok_desk_id', 'ok_desk_id', unique=True),
    )

    db_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Внутренний ИД')
    ok_desk_id: Mapped[int] = mapped_column(Integer, comment='ИД заявки в ОКДЕСК')
    req_data_db: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время создания записи в БД')
    title: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Название заявки')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата создания')
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Закончена')
    deadline_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Конечный срок')
    delay_to: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Продлена до')
    planned_reaction_a: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Плановая дата реакции')
    reacted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Время реакции')
    without_answer: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Без ответа')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Обновлено')
    status: Mapped[Optional[dict]] = mapped_column(JSON, comment='Статус заявки')
    type_req: Mapped[Optional[dict]] = mapped_column(JSON, comment='Тип заявки')
    priority: Mapped[Optional[dict]] = mapped_column(JSON, comment='Приоритет заявки')
    company: Mapped[Optional[dict]] = mapped_column(JSON, comment='Компания на ком заявка')
    contact: Mapped[Optional[dict]] = mapped_column(JSON, comment='Контакт')
    service_object: Mapped[Optional[dict]] = mapped_column(JSON, comment='Объект')
    agreement: Mapped[Optional[dict]] = mapped_column(JSON, comment='договор')
    equipments: Mapped[Optional[dict]] = mapped_column(JSON, comment='Оборудование')
    comments: Mapped[Optional[dict]] = mapped_column(JSON, comment='Коментарии')
    specifications: Mapped[Optional[dict]] = mapped_column(JSON, comment='Спецификации Заявки')
    observers: Mapped[Optional[dict]] = mapped_column(JSON, comment='Наблюдатели')
    assignee: Mapped[Optional[dict]] = mapped_column(JSON, comment='Исполнители')
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, comment='Параметры заявки')
    source: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Способ регистрации заявки')


class SensorVendor(Base):
    __tablename__ = 'sensor_vendor'
    __table_args__ = {'comment': 'Производители датчиков'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID изготовителя Датчиков')
    name: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Имя производителя')

    sensor_brands: Mapped[List['SensorBrands']] = relationship('SensorBrands', back_populates='sensor_vendor')


class SmsReply(Base):
    __tablename__ = 'sms_reply'
    __table_args__ = {'comment': 'Ответы от СМС'}

    reply_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    naming: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='От кого отправлен запрос')
    user_contact: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='На какой телефон отправлен запрос')
    internal_id: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='ID Отправки')
    created_reply_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Время создания записи')
    text_data: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='Ответ')
    received_at: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='получено по адресу')


class SmsSending(Base):
    __tablename__ = 'sms_sending'
    __table_args__ = {'comment': 'Таблица отправленных СМС'}

    sending_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_data: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Запрос')
    naming: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='От кого отправлен запрос')
    user_contact: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='На какой телефон отправлен запрос')
    created_send_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Время создании записи')
    internal_id: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='Уникальный ИД заявки')


class UserLogging(Base):
    __tablename__ = 'user_logging'
    __table_args__ = {'comment': 'Таблица для хранения логов действий пользователей Базы данных, '
                'например пользователя Битрикс или Разработчиков Махалова'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'))
    action_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'))
    action_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    action_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    old_val: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb3_unicode_ci'))
    new_val: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'))
    action_description: Mapped[Optional[str]] = mapped_column(TEXT)


t_Вытягивание_госНомеров_по_типу_А123АБ12 = Table(
    'Вытягивание госНомеров по типу А123АБ12', Base.metadata,
    Column('object_name', String(70)),
    Column('contragent_id', Integer)
)


t_Дубли_ICCID_по_маске_19_символов = Table(
    'Дубли ICCID по маске 19 символов', Base.metadata,
    Column('sim_iccid', String(19)),
    Column('count', BigInteger, server_default=text("'0'"))
)


t_Дубли_номеров = Table(
    'Дубли номеров', Base.metadata,
    Column('gn', String(25)),
    Column('ct', BigInteger, server_default=text("'0'"))
)


t_Не_привязанные_Объекты_к_КЛиентам = Table(
    'Не привязанные Объекты к КЛиентам', Base.metadata,
    Column('mon_sys_name', String(60)),
    Column('object_name', String(70)),
    Column('owner_contragent', String(200)),
    Column('owner_user', String(255))
)


t_Одинаковые_инн = Table(
    'Одинаковые инн', Base.metadata,
    Column('ca_inn', String(60)),
    Column('count', BigInteger, server_default=text("'0'"))
)


t_Одинаковые_логины = Table(
    'Одинаковые логины', Base.metadata,
    Column('login', String(60)),
    Column('count', BigInteger, server_default=text("'0'"))
)


t_Сим_1378___Терминал_4752 = Table(
    'Сим 1378 - Терминал 4752', Base.metadata,
    Column('device_serial', String(100)),
    Column('device_imei', String(60)),
    Column('terminal_date', DateTime),
    Column('name', String(200)),
    Column('ca_name', String(255)),
    Column('sim_iccid', String(40)),
    Column('sim_tel_number', String(40))
)


class Contragents(Base):
    __tablename__ = 'Contragents'
    __table_args__ = (
        ForeignKeyConstraint(['ca_holding_id'], ['holdings.holding_id'], name='fk_ca_holding_id'),
        Index('fk_ca_holding_id', 'ca_holding_id'),
        {'comment': 'Таблица для хранения информации о контрагентах по тз'}
    )

    ca_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ca_holding_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID холдинга')
    ca_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='НаименованиеПартнёра')
    ca_shortname: Mapped[Optional[str]] = mapped_column(VARCHAR(250), comment='НаименованиеПолноеПартнёра')
    ca_inn: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='ИНН')
    ca_kpp: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='КПП')
    ca_bill_account_num: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Расчетный счет ????????')
    ca_bill_account_bank_name: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Наименование банка ????')
    ca_bill_account_ogrn: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='ОГРН ????????')
    ca_edo_connect: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Обмен ЭДО ??????')
    ca_field_of_activity: Mapped[Optional[str]] = mapped_column(VARCHAR(260), comment='НаправлениеБизнесаКонтрагента')
    ca_type: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='ЮрФизЛицоПартёр')
    unique_onec_id: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='УникальныйИдентификаторПарнёра')
    registration_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Дата регистрации в 1С')
    key_manager: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Основной менеджер ')
    actual_address: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='Фактический адрес ')
    registered_office: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='Юридический адрес ')
    phone: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Телефон ')
    ca_uid_contragent: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='УникальныйИдентификаторКонтрагента')
    ca_name_contragent: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb3_unicode_ci'), comment='НаименованиеКонтрагента')
    service_manager: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Имя прикреплённого менеджера тех поддержки')
    ok_desk_id: Mapped[Optional[int]] = mapped_column(Integer, comment='id в ОК деске')
    ca_tarif: Mapped[Optional[str]] = mapped_column(VARCHAR(20), comment='Тариф Клиента')
    customer_training: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Обучен ли клиент по Сервисам.')

    ca_holding: Mapped[Optional['Holdings']] = relationship('Holdings', back_populates='Contragents')
    Login_users: Mapped[List['LoginUsers']] = relationship('LoginUsers', back_populates='contragent')
    ca_contacts: Mapped[List['CaContacts']] = relationship('CaContacts', back_populates='ca')
    ca_contracts: Mapped[List['CaContracts']] = relationship('CaContracts', back_populates='ca')
    ca_objects: Mapped[List['CaObjects']] = relationship('CaObjects', back_populates='contragent')
    clients_in_system_monitor: Mapped[List['ClientsInSystemMonitor']] = relationship('ClientsInSystemMonitor', back_populates='client')
    devices: Mapped[List['Devices']] = relationship('Devices', back_populates='contragent')
    discount_client_link: Mapped[List['DiscountClientLink']] = relationship('DiscountClientLink', back_populates='cl')
    equipment_warehouse: Mapped[List['EquipmentWarehouse']] = relationship('EquipmentWarehouse', back_populates='client')
    object_sensors: Mapped[List['ObjectSensors']] = relationship('ObjectSensors', back_populates='client')
    sender_logger: Mapped[List['SenderLogger']] = relationship('SenderLogger', back_populates='send_client')
    transfer_client: Mapped[List['TransferClient']] = relationship('TransferClient', back_populates='client')
    object_vehicles: Mapped[List['ObjectVehicles']] = relationship('ObjectVehicles', back_populates='vehicle_ca')
    sim_cards: Mapped[List['SimCards']] = relationship('SimCards', back_populates='contragent')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='client')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        ForeignKeyConstraint(['content_type_id'], ['django_content_type.id'], name='auth_permission_content_type_id_2f476e4b_fk_django_co'),
        Index('auth_permission_content_type_id_codename_01ab375a_uniq', 'content_type_id', 'codename', unique=True),
        {'comment': 'Таблица разрешений для пользователей ЦМС'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), comment='Название разрешения для пользователя ЦМС')
    content_type_id: Mapped[int] = mapped_column(Integer, comment='Возможность выполнять действия в ЦМС')
    codename: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'))

    content_type: Mapped['DjangoContentType'] = relationship('DjangoContentType', back_populates='auth_permission')
    auth_group_permissions: Mapped[List['AuthGroupPermissions']] = relationship('AuthGroupPermissions', back_populates='permission')
    auth_user_user_permissions: Mapped[List['AuthUserUserPermissions']] = relationship('AuthUserUserPermissions', back_populates='permission')


class AuthUserGroups(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['auth_group.id'], name='auth_user_groups_group_id_97559544_fk_auth_group_id'),
        ForeignKeyConstraint(['user_id'], ['auth_user.id'], name='auth_user_groups_user_id_6a12ed8b_fk_auth_user_id'),
        Index('auth_user_groups_group_id_97559544_fk_auth_group_id', 'group_id'),
        Index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'user_id', 'group_id', unique=True),
        {'comment': 'Таблица связи пользователей с группами в системе аутентификации '
                'ЦМС'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, comment='связь с пользователем ЦМС')
    group_id: Mapped[int] = mapped_column(Integer, comment='связь с группой пользователей ЦМС')

    group: Mapped['AuthGroup'] = relationship('AuthGroup', back_populates='auth_user_groups')
    user: Mapped['AuthUser'] = relationship('AuthUser', back_populates='auth_user_groups')


class DevicesBrands(Base):
    __tablename__ = 'devices_brands'
    __table_args__ = (
        ForeignKeyConstraint(['devices_vendor_id'], ['devices_vendor.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='devices_vendor_id_fk'),
        Index('devices_vendor_id_fk', 'devices_vendor_id'),
        {'comment': 'Таблица для хранения информации о моделях устройств'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'))
    devices_vendor_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Id Вендора терминалов')

    devices_vendor: Mapped[Optional['DevicesVendor']] = relationship('DevicesVendor', back_populates='devices_brands')
    devices: Mapped[List['Devices']] = relationship('Devices', back_populates='devices_brand')
    devices_commands: Mapped[List['DevicesCommands']] = relationship('DevicesCommands', back_populates='devices_brands')
    equipment_warehouse: Mapped[List['EquipmentWarehouse']] = relationship('EquipmentWarehouse', back_populates='terminal_model')
    transfer_client: Mapped[List['TransferClient']] = relationship('TransferClient', back_populates='device_model')


class DevicesLoggerCommands(Base):
    __tablename__ = 'devices_logger_commands'
    __table_args__ = (
        ForeignKeyConstraint(['programmer'], ['auth_user.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='programmer_id_fk'),
        Index('programmer_id_fk', 'programmer'),
        {'comment': 'Таблица для хранения журнала команд, отправленных на устройства '
                'через ЦМС не по ТЗ'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    command_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время отправки команды ')
    command_resresponse: Mapped[str] = mapped_column(VARCHAR(200), comment='Ответ на команду')
    command_send: Mapped[str] = mapped_column(VARCHAR(200), comment='Команда')
    programmer: Mapped[int] = mapped_column(Integer, comment='Кто отправил команду')
    terminal_imei: Mapped[str] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='imei терминала')

    auth_user: Mapped['AuthUser'] = relationship('AuthUser', back_populates='devices_logger_commands')


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'
    __table_args__ = (
        CheckConstraint('(`action_flag` >= 0)', name='django_admin_log_chk_1'),
        ForeignKeyConstraint(['content_type_id'], ['django_content_type.id'], name='django_admin_log_content_type_id_c4bce8eb_fk_django_co'),
        ForeignKeyConstraint(['user_id'], ['auth_user.id'], name='django_admin_log_user_id_c564eba6_fk_auth_user_id'),
        Index('django_admin_log_content_type_id_c4bce8eb_fk_django_co', 'content_type_id'),
        Index('django_admin_log_user_id_c564eba6_fk_auth_user_id', 'user_id'),
        {'comment': 'Таблица для хранения журнала действий администратора ЦМС'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_time: Mapped[datetime.datetime] = mapped_column(DATETIME(fsp=6), comment='Время операции')
    object_repr: Mapped[str] = mapped_column(VARCHAR(200), comment='что было изменено')
    action_flag: Mapped[int] = mapped_column(SMALLINT, comment='какое действие было выполнено')
    change_message: Mapped[str] = mapped_column(LONGTEXT, comment='на что изменено')
    user_id: Mapped[int] = mapped_column(Integer, comment='кто из пользователей ЦМС внёс изменения')
    object_id: Mapped[Optional[str]] = mapped_column(LONGTEXT, comment='id объекта Бд было произведено действие')
    content_type_id: Mapped[Optional[int]] = mapped_column(Integer, comment='в какой таблице были изменения')

    content_type: Mapped[Optional['DjangoContentType']] = relationship('DjangoContentType', back_populates='django_admin_log')
    user: Mapped['AuthUser'] = relationship('AuthUser', back_populates='django_admin_log')


class InspectTerminals(Base):
    __tablename__ = 'inspect_terminals'
    __table_args__ = (
        ForeignKeyConstraint(['monitoring_system'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='fk_monitoring_system_1'),
        Index('fk_monitoring_system_1', 'monitoring_system'),
        {'comment': 'Таблица по обходу терминалов'}
    )

    inspect_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID Инспекции')
    inspect_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Времяинспекции')
    type_term: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Тип терминала')
    imei: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='IMEIТерминала')
    iccid: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='ICCID СИМкарты')
    vehicleId: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='ID Как в СМ')
    vehicle_name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Имя Объекта')
    client_name: Mapped[Optional[str]] = mapped_column(String(400, 'utf8mb3_unicode_ci'), comment='Имя клиента как в 1С')
    client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ИД клиента из клиентов БД')
    iccid_in_db: Mapped[Optional[int]] = mapped_column(Integer, comment='Наличие Сим карты в нашей БД\r\n0-Клментская сим\r\n1-наша')
    if_change_imei: Mapped[Optional[int]] = mapped_column(Integer, comment='Будет ли изменён IMEI у сим\r\n0-нет\r\n1-да')
    old_sim_imei: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Если не сходится IMEI в СИМ заносится сюда ')
    monitoring_system: Mapped[Optional[int]] = mapped_column(Integer, comment='Система Мониторинга')

    monitoring_system_: Mapped[Optional['MonitoringSystem']] = relationship('MonitoringSystem', back_populates='inspect_terminals')


class Invoicing(Base):
    __tablename__ = 'invoicing'
    __table_args__ = (
        ForeignKeyConstraint(['system_monitorig_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='FK_puks_invoicing_system'),
        Index('FK_puks_invoicing_system', 'system_monitorig_id'),
        {'comment': 'Таблица для хранения информации о счетах-фактурах по объекту '
                'вытащенный из другой БД postgres'}
    )

    invoic_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    system_monitorig_id: Mapped[int] = mapped_column(Integer, comment='Связь к системе мониторинга из ПУКС')
    system_object_id: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ID в системе мониторинга из ПУКС')
    add_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='дата')
    puks_tarif: Mapped[Optional[int]] = mapped_column(Integer, comment='Тариф из ПУКС')

    system_monitorig: Mapped['MonitoringSystem'] = relationship('MonitoringSystem', back_populates='invoicing')


class SensorBrands(Base):
    __tablename__ = 'sensor_brands'
    __table_args__ = (
        ForeignKeyConstraint(['sensor_vendor_id'], ['sensor_vendor.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='vendor_id_fk'),
        Index('vendor_id_fk', 'sensor_vendor_id'),
        {'comment': 'Таблица моделей датчиков'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID Модели')
    name: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Название модели')
    sensor_vendor_id: Mapped[int] = mapped_column(Integer, comment='Связь к Фирме изготовителя')
    model_type: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Тип датчика: \r\n1 ДУТ.\r\n2 Температуры.\r\n3 Наклона.\r\n4 Индикатор.')

    sensor_vendor: Mapped['SensorVendor'] = relationship('SensorVendor', back_populates='sensor_brands')
    equipment_warehouse: Mapped[List['EquipmentWarehouse']] = relationship('EquipmentWarehouse', back_populates='sensor')
    object_sensors: Mapped[List['ObjectSensors']] = relationship('ObjectSensors', back_populates='sensor_model')


class LoginUsers(Base):
    __tablename__ = 'Login_users'
    __table_args__ = (
        ForeignKeyConstraint(['contragent_id'], ['Contragents.ca_id'], ondelete='SET NULL', onupdate='RESTRICT', name='contragent_idfk'),
        ForeignKeyConstraint(['system_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='system_idfk'),
        Index('contragent_idfk', 'contragent_id'),
        Index('system_idfk', 'system_id'),
        {'comment': 'Таблица для хранения информации о пользователях систем '
                'мониторинга'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_status: Mapped[int] = mapped_column(TINYINT, server_default=text("'1'"), comment='Состояние учётки 0-остановлена, 1-не подтверждена но активна, 2-подтверждена и активна 3 -тестовая\r\n4- Учётка для учёта ТС\r\n\r\n')
    client_name: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Старая колонка, при ведении excel таблицы')
    login: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='логин')
    email: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='почта')
    password: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='пароль')
    date_create: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='дата создания')
    system_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Ключ к системе мониторинга')
    contragent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID контрагента')
    comment_field: Mapped[Optional[str]] = mapped_column(String(270, 'utf8mb3_unicode_ci'), comment='Поле с комментариями')
    ca_uid: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='Уникальный id контрагента')
    is_billing: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Билинговый ли аккаунт\r\n0-не Билинговый\r\n1 - Билинговый')

    contragent: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='Login_users')
    system: Mapped[Optional['MonitoringSystem']] = relationship('MonitoringSystem', back_populates='Login_users')


class AuthGroupPermissions(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['auth_group.id'], name='auth_group_permissions_group_id_b120cbf9_fk_auth_group_id'),
        ForeignKeyConstraint(['permission_id'], ['auth_permission.id'], name='auth_group_permissio_permission_id_84c5c92e_fk_auth_perm'),
        Index('auth_group_permissio_permission_id_84c5c92e_fk_auth_perm', 'permission_id'),
        Index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'group_id', 'permission_id', unique=True),
        {'comment': 'Таблица связи групп пользователей ЦМС с разрешениями'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, comment='Связь с группой пользователей ЦМС')
    permission_id: Mapped[int] = mapped_column(Integer, comment='Связь с разрешениями действий в ЦМС')

    group: Mapped['AuthGroup'] = relationship('AuthGroup', back_populates='auth_group_permissions')
    permission: Mapped['AuthPermission'] = relationship('AuthPermission', back_populates='auth_group_permissions')


class AuthUserUserPermissions(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['permission_id'], ['auth_permission.id'], name='auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm'),
        ForeignKeyConstraint(['user_id'], ['auth_user.id'], name='auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id'),
        Index('auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm', 'permission_id'),
        Index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'user_id', 'permission_id', unique=True),
        {'comment': 'Таблица связи пользователей с разрешениями в системе '
                'аутентификации ЦМС'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    permission_id: Mapped[int] = mapped_column(Integer)

    permission: Mapped['AuthPermission'] = relationship('AuthPermission', back_populates='auth_user_user_permissions')
    user: Mapped['AuthUser'] = relationship('AuthUser', back_populates='auth_user_user_permissions')


class CaContacts(Base):
    __tablename__ = 'ca_contacts'
    __table_args__ = (
        ForeignKeyConstraint(['ca_id'], ['Contragents.ca_id'], name='ca_contacts_ibfk_1'),
        Index('ca_contact_cell_num', 'ca_contact_cell_num', unique=True),
        Index('ca_id', 'ca_id'),
        {'comment': 'Таблица для хранения контактной информации Клиентов по тз'}
    )

    ca_contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ca_id: Mapped[Optional[int]] = mapped_column(Integer, comment='связь с id компании')
    ca_contact_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Имя контактного лица')
    ca_contact_surname: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Фамилия контактного лица')
    ca_contact_middlename: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Отчество контактного лица')
    ca_contact_cell_num: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Сотовый телефон контакт. лица')
    ca_contact_work_num: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Рабочий телефон к.л.')
    ca_contact_email: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Электр.почт. к.л')
    ca_contact_position: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Должность к.л.')

    ca: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='ca_contacts')


class CaContracts(Base):
    __tablename__ = 'ca_contracts'
    __table_args__ = (
        ForeignKeyConstraint(['ca_id'], ['Contragents.ca_id'], name='ca_contracts_ibfk_1'),
        Index('ca_id', 'ca_id'),
        {'comment': 'Таблица для хранения информации о контрактах по тз'}
    )

    contract_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ca_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID контрагента')
    contract_type: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Тип договора\r\nя бы сделал choice')
    contract_num_prefix: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Префикс номера договора')
    contract_num: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Номер договора')
    contract_payment_term: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='условия оплаты')
    contract_payment_period: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Период оплаты')
    contract_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Дата заключения договора')
    contract_expired_date: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Дата завершения договора')

    ca: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='ca_contracts')


class CaObjects(Base):
    __tablename__ = 'ca_objects'
    __table_args__ = (
        ForeignKeyConstraint(['contragent_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='contragent_idfk_4'),
        ForeignKeyConstraint(['object_status'], ['object_statuses.status_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='status_idfk_3'),
        ForeignKeyConstraint(['sys_mon_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='mon_sys_idfk_2'),
        Index('contragent_idfk_4', 'contragent_id'),
        Index('mon_sys_idfk_2', 'sys_mon_id'),
        Index('status_idfk_3', 'object_status'),
        {'comment': 'Таблица для хранения информации об объектах из систем мониторинга'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sys_mon_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID системы мониторинга')
    sys_mon_object_id: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='ID объекта в системе мониторинга. Единственное за что можно зацепиться')
    object_name: Mapped[Optional[str]] = mapped_column(VARCHAR(70), comment='Название объекта')
    object_status: Mapped[Optional[int]] = mapped_column(Integer, comment='Статус объекта ссылается к статусам')
    object_add_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата добавления объекта')
    object_last_message: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата последнего сообщения')
    object_margin: Mapped[Optional[int]] = mapped_column(Integer, comment='Надбавка к базовой цене объекта')
    owner_contragent: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Хозяин контрагент, как в системе мониторинга.')
    owner_user: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Хозяин юзер. Логин пользователя в системе мониторинга')
    imei: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='идентификатор терминала')
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Когда изменён')
    object_created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата создания в системе мониторинга ')
    parent_id_sys: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Id клиента в системе мониторинга')
    contragent_id: Mapped[Optional[int]] = mapped_column(Integer)
    ca_uid: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Уникальный id контрагента')
    ok_desk_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID объекта в ОК-деске')
    addition_status_id: Mapped[Optional[int]] = mapped_column(TINYINT, comment='ID статуса доп')

    contragent: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='ca_objects')
    object_statuses: Mapped[Optional['ObjectStatuses']] = relationship('ObjectStatuses', back_populates='ca_objects')
    sys_mon: Mapped[Optional['MonitoringSystem']] = relationship('MonitoringSystem', back_populates='ca_objects')
    discount_obj_link: Mapped[List['DiscountObjLink']] = relationship('DiscountObjLink', back_populates='obj')
    group_object_retrans: Mapped[List['GroupObjectRetrans']] = relationship('GroupObjectRetrans', back_populates='obj')
    info_serv_obj: Mapped[List['InfoServObj']] = relationship('InfoServObj', back_populates='serv_obj_sys_mon')
    object_vehicles: Mapped[List['ObjectVehicles']] = relationship('ObjectVehicles', back_populates='vehicle_object')
    service_subscription_log: Mapped[List['ServiceSubscriptionLog']] = relationship('ServiceSubscriptionLog', back_populates='object')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='obj')


class ClientsInSystemMonitor(Base):
    __tablename__ = 'clients_in_system_monitor'
    __table_args__ = (
        ForeignKeyConstraint(['client_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='clients_id_fk1'),
        ForeignKeyConstraint(['system_monitor_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sys_mon_id_fk2'),
        Index('clients_id_fk1', 'client_id'),
        Index('sys_mon_id_fk2', 'system_monitor_id'),
        {'comment': 'Таблица для хранения информации об id клиентов и id родителей '
                'клиентов в СМ не по ТЗ'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_in_system_monitor: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Id клиента в системе мониторинга')
    name_in_system_monitor: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Имя клиента в системе мониторинга ')
    owner_id_sys_mon: Mapped[Optional[str]] = mapped_column(VARCHAR(200), comment='Id хозяина в системе мониторинга')
    system_monitor_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Id системы мониторинга ')
    client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='id клиента')

    client: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='clients_in_system_monitor')
    system_monitor: Mapped[Optional['MonitoringSystem']] = relationship('MonitoringSystem', back_populates='clients_in_system_monitor')


class Devices(Base):
    __tablename__ = 'devices'
    __table_args__ = (
        ForeignKeyConstraint(['contragent_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='contragent_ibfk_1'),
        ForeignKeyConstraint(['devices_brand_id'], ['devices_brands.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='device_brand_id_fk'),
        ForeignKeyConstraint(['itprogrammer_id'], ['auth_user.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='it_programmerfk'),
        ForeignKeyConstraint(['sys_mon_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sys_mon_idfk_2'),
        Index('contragent_ibfk_1', 'contragent_id'),
        Index('device_brand_id_fk', 'devices_brand_id'),
        Index('device_imei', 'device_imei', unique=True),
        Index('device_serial', 'device_serial', unique=True),
        Index('it_programmerfk', 'itprogrammer_id'),
        Index('sys_mon_idfk_2', 'sys_mon_id'),
        {'comment': 'Таблица для хранения информации об устройствах '
                'запрограммированных IT отделом не по тз'}
    )

    device_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_serial: Mapped[str] = mapped_column(VARCHAR(100), comment='Серийный номер устройства')
    device_imei: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='IMEI устройства')
    client_name: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Имя клиента')
    terminal_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата программирования терминала')
    devices_brand_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID Модели устройства ')
    name_it: Mapped[Optional[str]] = mapped_column(VARCHAR(50), comment='Имя програмировавшего терминал не актуальна')
    sys_mon_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID системы мониторинга')
    contragent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID контрагента')
    coment: Mapped[Optional[str]] = mapped_column(String(270, 'utf8mb3_unicode_ci'), comment='Коментарии')
    itprogrammer_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ссылается к программистам')
    device_owner: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Принадлежность терминала:\r\n--1 МЫ\r\n--0 Клиент')

    contragent: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='devices')
    devices_brand: Mapped[Optional['DevicesBrands']] = relationship('DevicesBrands', back_populates='devices')
    itprogrammer: Mapped[Optional['AuthUser']] = relationship('AuthUser', back_populates='devices')
    sys_mon: Mapped[Optional['MonitoringSystem']] = relationship('MonitoringSystem', back_populates='devices')
    devices_diagnostics: Mapped[List['DevicesDiagnostics']] = relationship('DevicesDiagnostics', back_populates='device')
    sim_cards: Mapped[List['SimCards']] = relationship('SimCards', back_populates='sim_device')


class DevicesCommands(Base):
    __tablename__ = 'devices_commands'
    __table_args__ = (
        ForeignKeyConstraint(['device_brand'], ['devices_brands.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='device_brand_idfk'),
        Index('device_brand_idfk', 'device_brand'),
        {'comment': 'Таблица для хранения информации о командах для устройств не по ТЗ'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    command: Mapped[Optional[str]] = mapped_column(VARCHAR(100), comment='сама команда')
    device_brand: Mapped[Optional[int]] = mapped_column(Integer, comment='Id брэнда терминала')
    method: Mapped[Optional[str]] = mapped_column(VARCHAR(10), comment='тип отправки команды\r\n0 - смс\r\n1 - интернет\r\n2 - любым')
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='описание действия команды')

    devices_brands: Mapped[Optional['DevicesBrands']] = relationship('DevicesBrands', back_populates='devices_commands')


class DiscountClientLink(Base):
    __tablename__ = 'discount_client_link'
    __table_args__ = (
        ForeignKeyConstraint(['cl_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='cl_id_FK_1'),
        ForeignKeyConstraint(['dis_id'], ['discount_client.dis_cl_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='dis_id_FK_2'),
        Index('cl_id_FK_1', 'cl_id'),
        Index('dis_id_FK_2', 'dis_id'),
        {'comment': 'Связка клиент скидки для клиентов'}
    )

    dis_cl_link_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID связи')
    cl_id: Mapped[int] = mapped_column(Integer, comment='ID клиента')
    dis_id: Mapped[int] = mapped_column(Integer, comment='ID скидки')

    cl: Mapped['Contragents'] = relationship('Contragents', back_populates='discount_client_link')
    dis: Mapped['DiscountClient'] = relationship('DiscountClient', back_populates='discount_client_link')


class EquipmentWarehouse(Base):
    __tablename__ = 'equipment_warehouse'
    __table_args__ = (
        ForeignKeyConstraint(['client_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='client_id_fk'),
        ForeignKeyConstraint(['sensor_id'], ['sensor_brands.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sensor_id_fk'),
        ForeignKeyConstraint(['terminal_model_id'], ['devices_brands.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='device_brand_fk'),
        Index('client_id_fk', 'client_id'),
        Index('device_brand_fk', 'terminal_model_id'),
        Index('sensor_id_fk', 'sensor_id'),
        Index('serial_number', 'serial_number', unique=True),
        {'comment': 'Таблица склада'}
    )

    id_unit: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='Идентификатор записи')
    add_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время регистрации добавления товара на склад')
    serial_number: Mapped[str] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Серийный номер')
    availability: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"), comment='Наличие на складе\r\n0- нет в наличии\r\n1- в наличии')
    whom_issued: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Кому выдан')
    affiliation: Mapped[int] = mapped_column(TINYINT, comment='Принадлежность к подразделению:\r\n0-Сервис\r\n1- мониторинг')
    terminal_model_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Реляционный id device')
    sensor_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Реляция id к датчикам')
    delivery_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата выдачи')
    client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Клиент как в 1С')
    comment: Mapped[Optional[str]] = mapped_column(VARCHAR(300), comment='коментарий')

    client: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='equipment_warehouse')
    sensor: Mapped[Optional['SensorBrands']] = relationship('SensorBrands', back_populates='equipment_warehouse')
    terminal_model: Mapped[Optional['DevicesBrands']] = relationship('DevicesBrands', back_populates='equipment_warehouse')


class ObjectSensors(Base):
    __tablename__ = 'object_sensors'
    __table_args__ = (
        ForeignKeyConstraint(['client_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sensor_client_id_fk'),
        ForeignKeyConstraint(['sensor_model_id'], ['sensor_brands.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sensor_brand_id_fk'),
        Index('sensor_brand_id_fk', 'sensor_model_id'),
        Index('sensor_client_id_fk', 'client_id'),
        Index('sensor_serial', 'sensor_serial', unique=True),
        {'comment': 'Датчик'}
    )

    sensor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_type: Mapped[int] = mapped_column(TINYINT, comment='Тип датчика:\r\n1ДУТ, 2Температуры3наклона')
    sensor_technology: Mapped[int] = mapped_column(TINYINT, comment='Подтип датчика:\r\n1аналоговый,2цифровой,\r\n3частотный')
    sensor_model_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Модель датчика к моделям')
    sensor_connect_type: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='Тип подключения')
    client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Связь с id Клиента')
    sensor_serial: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Серийный номер датчика')
    name_installer: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb3_unicode_ci'), comment='Имя монтажника')
    installer_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Id монтажника')

    client: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='object_sensors')
    sensor_model: Mapped[Optional['SensorBrands']] = relationship('SensorBrands', back_populates='object_sensors')


class SenderLogger(Base):
    __tablename__ = 'sender_logger'
    __table_args__ = (
        ForeignKeyConstraint(['send_client_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='send_client_id_FK'),
        Index('send_client_id_FK', 'send_client_id'),
        {'comment': 'Таблица с рассылками'}
    )

    send_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    send_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время события рассылки')
    send_mail: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb3_unicode_ci'), comment='Почта рассылки')
    send_client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='Ид клиента БД_2')
    send_client_id_okdesk: Mapped[Optional[int]] = mapped_column(Integer, comment='ID клиента ОКДЕСК')
    send_req_okdesk_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID заявки в окдеск')
    send_text: Mapped[Optional[str]] = mapped_column(LONGTEXT, comment='Текст рассылки')

    send_client: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='sender_logger')


class TransferClient(Base):
    __tablename__ = 'transfer_client'
    __table_args__ = (
        ForeignKeyConstraint(['client_id'], ['Contragents.ca_id'], name='transfer_client_FK_contragent'),
        ForeignKeyConstraint(['current_sys_mon'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='current_sys_mon_FK'),
        ForeignKeyConstraint(['device_model_id'], ['devices_brands.id'], name='transfer_client_FK_device_type_brand'),
        ForeignKeyConstraint(['tranfer_sys_mon_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sys_mon_trans_FK'),
        Index('current_sys_mon_idx', 'current_sys_mon'),
        Index('sys_mon_trans_FK', 'tranfer_sys_mon_id'),
        Index('transfer_client_FK_contragent', 'client_id'),
        Index('transfer_client_FK_device_type_brand', 'device_model_id')
    )

    trans_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Id перевода')
    client_id: Mapped[int] = mapped_column(Integer, comment='Id клиента')
    tranfer_sys_mon_id: Mapped[int] = mapped_column(Integer, comment='Id системы мониторинга на которую нужен перевод.')
    start_trans: Mapped[datetime.datetime] = mapped_column(DateTime, comment='Начало перевода')
    end_trans: Mapped[datetime.datetime] = mapped_column(DateTime, comment='Окончание перевода')
    terminal_command: Mapped[str] = mapped_column(String(200), comment='Команда терминала')
    command_type: Mapped[int] = mapped_column(TINYINT, comment='Тип комманды через что отправлять: 0 - API, 1 - sms')
    device_model_id: Mapped[int] = mapped_column(Integer, comment='Id модели терминала')
    current_sys_mon: Mapped[int] = mapped_column(Integer, comment='Текущая система мониторинга(с какой системы перевести)')

    client: Mapped['Contragents'] = relationship('Contragents', back_populates='transfer_client')
    monitoring_system: Mapped['MonitoringSystem'] = relationship('MonitoringSystem', foreign_keys=[current_sys_mon], back_populates='transfer_client')
    device_model: Mapped['DevicesBrands'] = relationship('DevicesBrands', back_populates='transfer_client')
    tranfer_sys_mon: Mapped['MonitoringSystem'] = relationship('MonitoringSystem', foreign_keys=[tranfer_sys_mon_id], back_populates='transfer_client_')


class DevicesDiagnostics(Base):
    __tablename__ = 'devices_diagnostics'
    __table_args__ = (
        ForeignKeyConstraint(['device_id'], ['devices.device_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='devices_id_fk_deagnostic_1'),
        ForeignKeyConstraint(['programmer_id'], ['auth_user.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='programmer_id_fk_deagnostic_2'),
        Index('devices_id_fk_deagnostic_1', 'device_id'),
        Index('programmer_id_fk_deagnostic_2', 'programmer_id'),
        {'comment': 'Таблица для хранения информации о диагностике устройств не по тз'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, comment='Отношение к терминалам')
    programmer_id: Mapped[int] = mapped_column(Integer, comment='Отношение к программистам')
    brought: Mapped[int] = mapped_column(TINYINT, comment='Принесён:\r\n0-от клиента\r\n1-после ремонта')
    comment: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Коментарий')
    accept_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Дата приёма')
    transfer_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата передачи')
    whom_tranfer: Mapped[Optional[int]] = mapped_column(TINYINT, comment='Куда отдан:\r\n0 - клиенту\r\n1 - в ремонт')
    USB_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка USB')
    PWR_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка основного питания')
    PWR_AKB_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка резервного питания')
    FIRMWARE_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка прошивки')
    SATS_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка спутников')
    GSM_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка GSM')
    ONLINE_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка online')
    P485_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка 485 порта')
    DIGIT_PORT_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка цифровых входов')
    ANALOG_PORT_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек проверка аналоговых входов')
    GSM_antenna_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек GSM антенна в комплекте')
    GPS_antenna_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек GPS антенна в комплекте')
    CABEL_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек разъем питания в комплекте')
    SIM_check: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='Чек сим в комплекте')
    USB_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке USB')
    PWR_comment: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Комментарий к проверке основного питания')
    PWR_AKB_comment: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Комментарий к проверке резервного питания')
    FIRMWARE_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке прошивки')
    SATS_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке наличия связи со спутниками')
    GSM_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке связи GSM')
    ONLINE_comment: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Комментарий к проверке онлайна в системе мониторинга')
    P485_comment: Mapped[Optional[str]] = mapped_column(VARCHAR(60), comment='Комментарий к проверке 485 порта')
    DIGIT_PORT_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке цифровых портов')
    ANALOG_PORT_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к проверке аналоговых портов')
    SIM_comment: Mapped[Optional[str]] = mapped_column(String(60, 'utf8mb3_unicode_ci'), comment='Комментарий к SIM карте')

    device: Mapped['Devices'] = relationship('Devices', back_populates='devices_diagnostics')
    programmer: Mapped['AuthUser'] = relationship('AuthUser', back_populates='devices_diagnostics')


class DiscountObjLink(Base):
    __tablename__ = 'discount_obj_link'
    __table_args__ = (
        ForeignKeyConstraint(['dis_id'], ['discount_obj.dis_obj_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='dis_dis_id_FK_2'),
        ForeignKeyConstraint(['obj_id'], ['ca_objects.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='dis_obj_id_FK_1'),
        Index('dis_dis_id_FK_2', 'dis_id'),
        Index('dis_obj_id_FK_1', 'obj_id')
    )

    dis_obj_link_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    obj_id: Mapped[int] = mapped_column(Integer, comment='ID объекта')
    dis_id: Mapped[int] = mapped_column(Integer, comment='ID скидки под объекты')

    dis: Mapped['DiscountObj'] = relationship('DiscountObj', back_populates='discount_obj_link')
    obj: Mapped['CaObjects'] = relationship('CaObjects', back_populates='discount_obj_link')


class GroupObjectRetrans(Base):
    __tablename__ = 'group_object_retrans'
    __table_args__ = (
        ForeignKeyConstraint(['obj_id'], ['ca_objects.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='object_FK'),
        ForeignKeyConstraint(['retr_id'], ['object_retranslators.retranslator_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='retrans_FK'),
        Index('object_FK', 'obj_id'),
        Index('retrans_FK', 'retr_id'),
        {'comment': 'Таблица для сведения объектов и ретрансляторов'}
    )

    id_group: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Айдишник')
    obj_id: Mapped[int] = mapped_column(Integer, comment='Айдишник объекта')
    retr_id: Mapped[int] = mapped_column(Integer, comment='Айдишник ретранслятора')

    obj: Mapped['CaObjects'] = relationship('CaObjects', back_populates='group_object_retrans')
    retr: Mapped['ObjectRetranslators'] = relationship('ObjectRetranslators', back_populates='group_object_retrans')


class InfoServObj(Base):
    __tablename__ = 'info_serv_obj'
    __table_args__ = (
        ForeignKeyConstraint(['info_obj_serv_id'], ['information_services.serv_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='serv_id_FK'),
        ForeignKeyConstraint(['monitoring_sys'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sys_mon_inf_FK'),
        ForeignKeyConstraint(['serv_obj_sys_mon_id'], ['ca_objects.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='obj_in_serv_id_FK'),
        Index('obj_in_serv_id_FK', 'serv_obj_sys_mon_id'),
        Index('serv_id_FK', 'info_obj_serv_id'),
        Index('sys_mon_inf_FK', 'monitoring_sys'),
        {'comment': 'Объекты с информационными сервисами'}
    )

    serv_obj_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID подписки')
    serv_obj_sys_mon_id: Mapped[int] = mapped_column(Integer, comment='Внутренний ID объекта\r\nБазы данных из СМ')
    info_obj_serv_id: Mapped[int] = mapped_column(Integer, comment='ID ведёт сервисам')
    subscription_start: Mapped[datetime.datetime] = mapped_column(DateTime, comment='Время начала подписки')
    service_counter: Mapped[int] = mapped_column(Integer, comment='СЧЁТЧИК услуг\r\n0- мгновенно\r\n1-раз в день\r\n2-раз в неделю\r\n3-раз в месяц')
    stealth_type: Mapped[int] = mapped_column(TINYINT, comment='0 - автоматический\r\n1 - с проверкой')
    monitoring_sys: Mapped[int] = mapped_column(Integer, comment='Система мониторинга')
    sys_id_obj: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='ID объекта в системе мониторинга')
    sys_login: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Логин пользователя от системы мониторинга')
    sys_password: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Пароль пользователя от СМ')
    grouping_sign: Mapped[int] = mapped_column(TINYINT, server_default=text("'0'"), comment='Есть ли группировка')
    subscription_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Время окончания подписки')
    tel_num_user: Mapped[Optional[str]] = mapped_column(VARCHAR(11), comment='Телефонный номер с которого созданна услуга')
    send_meth: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='Способ отправки 0 - ОКДЕСК\r\n1 - MAIL')
    testing_status: Mapped[Optional[int]] = mapped_column(TINYINT, server_default=text("'0'"), comment='0 - ТЕСТ\r\n1 - Абонентка')

    info_obj_serv: Mapped['InformationServices'] = relationship('InformationServices', back_populates='info_serv_obj')
    monitoring_system: Mapped['MonitoringSystem'] = relationship('MonitoringSystem', back_populates='info_serv_obj')
    serv_obj_sys_mon: Mapped['CaObjects'] = relationship('CaObjects', back_populates='info_serv_obj')


class ObjectVehicles(Base):
    __tablename__ = 'object_vehicles'
    __table_args__ = (
        ForeignKeyConstraint(['vehicle_ca_id'], ['Contragents.ca_id'], name='object_vehicles_ibfk_2'),
        ForeignKeyConstraint(['vehicle_object_id'], ['ca_objects.id'], name='object_vehicles_ibfk_1'),
        Index('vehicle_ca_id', 'vehicle_ca_id'),
        Index('vehicle_gos_nomer', 'vehicle_gos_nomer', unique=True),
        Index('vehicle_object_id', 'vehicle_object_id'),
        {'comment': 'Таблица для хранения информации об объектах-транспортных '
                'средствах'}
    )

    vehicle_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_gos_nomer: Mapped[str] = mapped_column(VARCHAR(25), comment='госномер')
    vehicle_object_id: Mapped[Optional[int]] = mapped_column(Integer, comment='привязка к объекту')
    vehicle_ca_id: Mapped[Optional[int]] = mapped_column(Integer, comment='привязка к контрагенту')
    vehicle_vendor_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='производитель тс')
    vehicle_vendor_model: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='марка тс')
    vehicle_year_of_manufacture: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='дата выпуска тс')
    vehicle_gos_nomer_region: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='регион')
    vehicle_type: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='тип тс')
    vehicle_vin: Mapped[Optional[str]] = mapped_column(VARCHAR(255), comment='вин')

    vehicle_ca: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='object_vehicles')
    vehicle_object: Mapped[Optional['CaObjects']] = relationship('CaObjects', back_populates='object_vehicles')


class ServiceSubscriptionLog(Base):
    __tablename__ = 'service_subscription_log'
    __table_args__ = (
        ForeignKeyConstraint(['object_id'], ['ca_objects.id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_log_object'),
        ForeignKeyConstraint(['user_id'], ['auth_user.id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_log_user'),
        Index('idx_change_time', 'change_time'),
        Index('idx_object_id', 'object_id'),
        Index('idx_user_id', 'user_id'),
        {'comment': 'Лог изменений сервисных подписок'}
    )

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID записи лога')
    user_id: Mapped[int] = mapped_column(Integer, comment='ID пользователя')
    username: Mapped[str] = mapped_column(VARCHAR(150), comment='Имя пользователя')
    object_id: Mapped[int] = mapped_column(Integer, comment='ID объекта')
    action: Mapped[str] = mapped_column(VARCHAR(50), comment='Действие')
    changes: Mapped[Optional[str]] = mapped_column(TEXT, comment='Изменения в JSON')
    change_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='Время изменения')

    object: Mapped['CaObjects'] = relationship('CaObjects', back_populates='service_subscription_log')
    user: Mapped['AuthUser'] = relationship('AuthUser', back_populates='service_subscription_log')


class SimCards(Base):
    __tablename__ = 'sim_cards'
    __table_args__ = (
        ForeignKeyConstraint(['contragent_id'], ['Contragents.ca_id'], ondelete='SET NULL', onupdate='SET NULL', name='contragent_idfk_3'),
        ForeignKeyConstraint(['itprogrammer_id'], ['auth_user.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='it_programmer_idfk'),
        ForeignKeyConstraint(['sim_cell_operator'], ['Cell_operator.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='operator_cell_idfk_3'),
        ForeignKeyConstraint(['sim_device_id'], ['devices.device_id'], name='sim_cards_ibfk_1'),
        Index('contragent_idfk_3', 'contragent_id'),
        Index('it_programmer_idfk', 'itprogrammer_id'),
        Index('operator_cell_idfk_3', 'sim_cell_operator'),
        Index('sim_device_id', 'sim_device_id'),
        Index('sim_iccid', 'sim_iccid', unique=True)
    )

    sim_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sim_iccid: Mapped[Optional[str]] = mapped_column(VARCHAR(40), comment='ICCID')
    sim_tel_number: Mapped[Optional[str]] = mapped_column(VARCHAR(40), comment='телефонный номер сим')
    client_name: Mapped[Optional[str]] = mapped_column(VARCHAR(270), comment='Имя клиента')
    sim_cell_operator: Mapped[Optional[int]] = mapped_column(Integer, comment='Сотовый оператор(надо по ID)')
    sim_owner: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment="1, 'Мы'\r\n0, 'Клиент'")
    sim_device_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID к девайсам(devices)')
    sim_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Дата регистрации сим')
    status: Mapped[Optional[int]] = mapped_column(Integer, comment='Активность симки:\r\n0-списана, 1-активна, 2-приостан, 3-первичная блокировка, 4-статус неизвестен,\r\n5 - Сезонная блокировка')
    terminal_imei: Mapped[Optional[str]] = mapped_column(String(25, 'utf8mb3_unicode_ci'), comment='IMEI терминала в который вставлена симка')
    contragent_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID контрагента')
    ca_uid: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Уникальный id контрагента')
    itprogrammer_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID сотрудника програмировавшего терминал')
    block_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Начало блокировки')
    block_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Предварительный конец блокировки')

    contragent: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='sim_cards')
    itprogrammer: Mapped[Optional['AuthUser']] = relationship('AuthUser', back_populates='sim_cards')
    Cell_operator: Mapped[Optional['CellOperator']] = relationship('CellOperator', back_populates='sim_cards')
    sim_device: Mapped[Optional['Devices']] = relationship('Devices', back_populates='sim_cards')
    billing: Mapped[List['Billing']] = relationship('Billing', back_populates='sim')


class Billing(Base):
    __tablename__ = 'billing'
    __table_args__ = (
        ForeignKeyConstraint(['client_id'], ['Contragents.ca_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='client_FK_5'),
        ForeignKeyConstraint(['obj_id'], ['ca_objects.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='obj_FK_3'),
        ForeignKeyConstraint(['obj_status_id'], ['object_statuses.status_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='obj_status_id_FK_6'),
        ForeignKeyConstraint(['retrans_id'], ['object_retranslators.retranslator_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='retrans_FK_2'),
        ForeignKeyConstraint(['sim_id'], ['sim_cards.sim_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sim_FK_4'),
        ForeignKeyConstraint(['sys_mon_id'], ['monitoring_system.mon_sys_id'], ondelete='RESTRICT', onupdate='RESTRICT', name='sys_mon_FK_1'),
        Index('client_FK_5', 'client_id'),
        Index('obj_FK_3', 'obj_id'),
        Index('obj_status_id_FK_6', 'obj_status_id'),
        Index('retrans_FK_2', 'retrans_id'),
        Index('sim_FK_4', 'sim_id'),
        Index('sys_mon_FK_1', 'sys_mon_id'),
        {'comment': 'Таблица снимок параметров билинга за день'}
    )

    bil_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID билинга')
    sys_mon_id: Mapped[int] = mapped_column(Integer, comment='ID системы мониторинга')
    sys_mon_price: Mapped[int] = mapped_column(Integer, comment='Стоимость СМ для КЛ')
    obj_id: Mapped[int] = mapped_column(Integer, comment='ID объекта в БД')
    obj_name: Mapped[str] = mapped_column(VARCHAR(100), comment='Название объекта')
    obj_status_id: Mapped[int] = mapped_column(Integer, comment='ID статуса объекта')
    record_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='Время создания записи')
    obj_status_name: Mapped[str] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Имя статуса объекта')
    obj_group_id: Mapped[str] = mapped_column(String(400, 'utf8mb3_unicode_ci'), comment='ИД группы объектов')
    obj_id_in_sys: Mapped[str] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='ID объекта в системе мониторинга')
    sys_mon_name: Mapped[str] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='Название системы мониторинга')
    retrans_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID ретрансляции')
    retrans_name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Название ретрансляции')
    retrans_price: Mapped[Optional[int]] = mapped_column(Integer, comment='Цена ретрансляции')
    sim_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID СИМКАРТЫ')
    sim_operat_name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb3_unicode_ci'), comment='Имя оператора')
    sim_price: Mapped[Optional[int]] = mapped_column(Integer, comment='Цена сим для КЛ')
    client_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID клиента')
    client_name: Mapped[Optional[str]] = mapped_column(String(300, 'utf8mb3_unicode_ci'), comment='Имя клиента')
    client_inn: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='ИНН Клиента')
    discount_client: Mapped[Optional[dict]] = mapped_column(JSON, comment="СКИДКИ КЛИЕНТА\r\n[{'dis_id': 1, 'dis_name': 'Лояльность'},\r\n {'dis_id': 2, 'dis_name': 'Кол-во объектов > 50'},\r\n]")
    discount_client_rate: Mapped[Optional[int]] = mapped_column(Integer, comment='Итоговый процент Скидки')
    discount_obj: Mapped[Optional[dict]] = mapped_column(JSON, comment="СКИДКИ КЛИЕНТА [{'dis_id': 1, 'dis_name': 'Лояльность'}, {'dis_id': 2, 'dis_name': 'Дружественный'}, ]")
    discount_obj_rate: Mapped[Optional[int]] = mapped_column(Integer, comment='Процент скидок на объект')
    obj_group_name: Mapped[Optional[str]] = mapped_column(VARCHAR(400), comment='Название группы объектов как в СМ')
    client_login: Mapped[Optional[str]] = mapped_column(VARCHAR(400), comment='Логин клиента')
    client_kpp: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb3_unicode_ci'), comment='Клиентский КПП')
    total_sum: Mapped[Optional[int]] = mapped_column(Integer, comment='Итоговая сумма')
    obj_imei: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb3_unicode_ci'), comment='IMEI объекта')

    client: Mapped[Optional['Contragents']] = relationship('Contragents', back_populates='billing')
    obj: Mapped['CaObjects'] = relationship('CaObjects', back_populates='billing')
    obj_status: Mapped['ObjectStatuses'] = relationship('ObjectStatuses', back_populates='billing')
    retrans: Mapped[Optional['ObjectRetranslators']] = relationship('ObjectRetranslators', back_populates='billing')
    sim: Mapped[Optional['SimCards']] = relationship('SimCards', back_populates='billing')
    sys_mon: Mapped['MonitoringSystem'] = relationship('MonitoringSystem', back_populates='billing')
