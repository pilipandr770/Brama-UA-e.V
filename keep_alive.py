"""
Скрипт для предотвращения "засыпания" приложения на бесплатном тарифе Render
Запускайте этот скрипт на другом сервере или локально по расписанию через cron
каждые 10-14 минут, чтобы поддерживать приложение активным.
"""
import requests
import time
import sys
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("keep_alive.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# URL вашего приложения на Render
APP_URL = "https://brama-portal.onrender.com"

def ping_app():
    """Отправляет запрос на главную страницу сайта для поддержания активности"""
    try:
        start_time = time.time()
        response = requests.get(f"{APP_URL}/", timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            duration = round(end_time - start_time, 2)
            logging.info(f"Успешный пинг! Статус: {response.status_code}, время ответа: {duration} сек.")
            return True
        else:
            logging.warning(f"Пинг выполнен, но получен необычный статус: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {str(e)}")
        return False

def main():
    """Основная функция, выполняет пинг приложения"""
    logging.info(f"Запуск пинга приложения {APP_URL} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = ping_app()
    
    if success:
        logging.info("Приложение поддерживается активным")
    else:
        logging.warning("Не удалось поддержать активность приложения")

if __name__ == "__main__":
    main()