"""
Улучшенный механизм логирования для отслеживания ошибок.
Помогает диагностировать проблемы в продакшн-среде.
"""

import logging
from flask import Flask, request, render_template
import os
import traceback
from datetime import datetime

def setup_enhanced_logging(app: Flask):
    """
    Настраивает расширенное логирование для приложения Flask.
    
    Добавляет:
    - Запись запросов в лог файл
    - Детальное логирование ошибок с контекстом
    - Вращение логов
    - Сохранение стека вызовов для отладки
    """
    # Создаем директорию для логов, если она не существует
    log_dir = os.path.join(app.root_path, 'logs')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            app.logger.warning(f"Не удалось создать директорию для логов: {e}")
            log_dir = app.root_path
    
    # Настройка форматирования логов
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    try:
        # Файловый хендлер для всех логов
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Отдельный файловый хендлер для ошибок
        error_log_file = os.path.join(log_dir, 'errors.log')
        error_file_handler = logging.FileHandler(error_log_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        
        # Добавляем хендлеры к логгеру приложения
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_file_handler)
        
        # Устанавливаем уровень логирования
        app.logger.setLevel(logging.INFO)
        
    except Exception as e:
        app.logger.error(f"Ошибка при настройке логирования: {e}")
    
    @app.before_request
    def log_request_info():
        """Логирование информации о запросе"""
        app.logger.info(f"Request: {request.method} {request.path} [IP: {request.remote_addr}]")
    
    @app.after_request
    def log_response_info(response):
        """Логирование информации об ответе"""
        app.logger.info(f"Response: {response.status_code}")
        return response
    
    # Настраиваем обработчик для необработанных исключений
    @app.errorhandler(Exception)
    def log_exception(e):
        """Детальное логирование необработанных исключений"""
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Собираем подробную информацию о запросе
        request_info = {
            'path': request.path,
            'method': request.method,
            'user_agent': request.user_agent.string,
            'ip': request.remote_addr,
            'headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'args': dict(request.args),
            'form': dict(request.form) if request.form else None
        }
        
        # Получаем стек вызовов
        error_traceback = traceback.format_exc()
        
        # Логируем подробную информацию
        app.logger.error(f"EXCEPTION [Request: {request.method} {request.path}]")
        app.logger.error(f"REQUEST DETAILS: {request_info}")
        app.logger.error(f"TRACEBACK: {error_traceback}")
        
        # Сохраняем детальный отчет об ошибке в отдельный файл
        try:
            error_report_file = os.path.join(log_dir, f'error_report_{now}.txt')
            with open(error_report_file, 'w') as f:
                f.write(f"ОШИБКА: {str(e)}\n")
                f.write(f"ВРЕМЯ: {now}\n")
                f.write(f"ПУТЬ: {request.path}\n")
                f.write(f"МЕТОД: {request.method}\n")
                f.write(f"IP: {request.remote_addr}\n")
                f.write(f"USER AGENT: {request.user_agent.string}\n\n")
                f.write(f"ЗАГОЛОВКИ:\n{dict(request.headers)}\n\n")
                f.write(f"COOKIES:\n{dict(request.cookies)}\n\n")
                f.write(f"ПАРАМЕТРЫ GET:\n{dict(request.args)}\n\n")
                f.write(f"ПАРАМЕТРЫ POST:\n{dict(request.form) if request.form else None}\n\n")
                f.write(f"СТЕК ВЫЗОВОВ:\n{error_traceback}")
        except Exception as write_err:
            app.logger.error(f"Не удалось сохранить отчет об ошибке: {write_err}")
        
        # Преобразуем ошибку в понятный для пользователя ответ
        return render_template('error.html', 
                              error_code=500, 
                              error_title="Ошибка приложения",
                              error_message="Произошла непредвиденная ошибка.", 
                              error_details=error_traceback if app.debug else None), 500
    
    app.logger.info("Расширенное логирование настроено")