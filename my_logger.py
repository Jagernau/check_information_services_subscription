import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Создание обработчика для записи в файл
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)
