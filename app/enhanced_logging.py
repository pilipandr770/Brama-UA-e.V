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
    # Определяем директорию для логов в зависимости от окружения
    # На Render используем /tmp для временных файлов
    is_render = os.environ.get('RENDER') == 'true'
    
    if is_render:
        # На Render записываем логи в /tmp
        log_dir = '/tmp'
        app.logger.info(f"Запуск на платформе Render, логи будут сохраняться в {log_dir}")
    else:
        # В других средах используем каталог logs в директории приложения
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
        # Проверяем возможность записи в директорию для логов
        test_file_path = os.path.join(log_dir, 'test_write.tmp')
        try:
            with open(test_file_path, 'w') as f:
                f.write('test')
            os.remove(test_file_path)
            app.logger.info(f"Проверка записи в {log_dir} выполнена успешно")
            can_write_logs = True
        except Exception as write_test_err:
            app.logger.warning(f"Невозможно записать в {log_dir}: {write_test_err}")
            can_write_logs = False
        
        if can_write_logs:
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
            
            app.logger.info(f"Логирование в файлы настроено: {log_file}, {error_log_file}")
        else:
            # Если запись в файлы невозможна, логируем только в консоль
            app.logger.warning("Логирование в файлы недоступно, используется только консольное логирование")
            
            # Добавляем консольный обработчик, если его еще нет
            has_console_handler = False
            for handler in app.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream.name == '<stderr>':
                    has_console_handler = True
                    break
            
            if not has_console_handler:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                app.logger.addHandler(console_handler)
        
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
    
    # Функция для логирования ошибок, НЕ регистрируем обработчик,
    # так как он уже определен в __init__.py
    def log_exception(e, error_code=500):
        """Детальное логирование исключений без регистрации обработчика"""
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Проверяем, доступен ли объект request
        if not hasattr(request, 'path'):
            app.logger.error(f"Exception occurred outside request context: {str(e)}")
            return
        
        # Собираем подробную информацию о запросе
        try:
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
            app.logger.error(f"EXCEPTION [{error_code}] [Request: {request.method} {request.path}]")
            app.logger.error(f"ERROR: {str(e)}")
            app.logger.error(f"REQUEST DETAILS: {request_info}")
            app.logger.error(f"TRACEBACK: {error_traceback}")
            
            # Сохраняем детальный отчет об ошибке в отдельный файл,
            # только если включен режим отладки или переменная среды SAVE_ERROR_REPORTS=true
            if app.debug or os.getenv("SAVE_ERROR_REPORTS", "false").lower() in ("1", "true", "yes"):
                try:
                    error_report_file = os.path.join(log_dir, f'error_report_{now}.txt')
                    with open(error_report_file, 'w') as f:
                        f.write(f"ОШИБКА: {str(e)}\n")
                        f.write(f"КОД ОШИБКИ: {error_code}\n")
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
        except Exception as log_err:
            app.logger.error(f"Ошибка при логировании исключения: {log_err}")
            
    # Регистрируем функцию логирования в приложении для использования в __init__.py
    app.log_exception = log_exception
    
    app.logger.info("Расширенное логирование настроено")