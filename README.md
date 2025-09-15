# Brama UA e.V. – Портал громади та проєктів

Проєкт Brama UA e.V. — це веб‑портал для підтримки української громади в Німеччині: подання соціальних проєктів, модерація, прозоре голосування, галерея та публічні результати. Портал підтримує мультимовність і ролі користувачів.

---

## Основні можливості

- Реєстрація/логін і особистий кабінет (Flask‑Login)
- Подання проєктів із зображенням та файлами
- Модерація і статуси проєктів (pending/approved/…)
- Голосування (модель Vote), підрахунок результатів
- Галерея та динамічні контент‑блоки
- Мультимовність: uk / de / en (Flask‑Babel)
- WebSocket‑підключення (Flask‑SocketIO) для інтерактивних можливостей

---

## Технології

- Python 3.12+ (перевірено на 3.13 у Windows)
- Flask, Flask‑SQLAlchemy, Flask‑Migrate, Flask‑Login
- Flask‑Babel (i18n), Jinja2
- SQLite (локально за замовчуванням) / PostgreSQL (продакшн)
- Socket.IO (eventlet), python‑dotenv

---

## Структура проєкту (скорочено)

```
Brama-UA-e.V/
├─ app/
│  ├─ models/           # SQLAlchemy‑моделі (User, Project, Vote, Block, ...)
│  ├─ routes/           # Blueprints (main, admin, api)
│  ├─ templates/        # Jinja2‑шаблони
│  ├─ static/           # CSS, JS, зображення
│  ├─ babel.py          # i18n‑ініціалізація
│  └─ __init__.py       # create_app(), реєстрація розширень і blueprints
├─ migrations/          # Alembic‑міграції
├─ config.py            # Конфіг (БД, локаль, пошта, BASE_URL)
├─ run.py               # Точка входу (SocketIO + eventlet)
├─ requirements.txt     # Залежності Python
└─ README.md            # Цей файл
```

---

## Вимоги

- Python 3.12 або новіший
- PowerShell (Windows) або Bash (Linux/macOS)

---

## Налаштування оточення

Створіть файл `.env` у корені проєкту. Приклади змінних:

```
# Безпека
SECRET_KEY=change-me

# База даних
# Для продакшну (Render/Postgres):
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
# DB_SCHEMA=public  # або ваша схема, напр. brama

# Для локальної розробки — можна не вказувати (використається SQLite site.db)

# Базовий URL (посилання в листах тощо)
BASE_URL=http://localhost:8080

# Налаштування пошти (опційно)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@brama-ua.org
```

Примітки:
- Якщо `DATABASE_URL` не заданий — застосунок використовує SQLite файл `site.db` у корені репозиторію (див. `config.py`).
- Для PostgreSQL можна задати `DB_SCHEMA` (за замовчуванням `public`). Для Render часто достатньо `DATABASE_URL`.

---

## Встановлення та запуск (Windows / PowerShell)

1) Створіть та активуйте віртуальне середовище:

```powershell
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

2) Встановіть залежності:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

3) Ініціалізуйте/оновіть БД міграціями Alembic:

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
```

4) Запустіть сервер Socket.IO (eventlet) через `run.py`:

```powershell
py run.py
```

Сервер стартує на `http://0.0.0.0:8080` (локально відкривайте `http://localhost:8080`).
Щоб змінити порт:

```powershell
$env:PORT="8081"
py run.py
```

---

## Облікові записи та адміністрування

- Скрипт `make_admin.py` допомагає призначити адміністратора (за потреби адаптуйте під вашу модель користувача).
- В адмін‑панелі доступні дії модерації, керування блоками/галереєю тощо (див. маршрути в `app/routes/admin.py`).

---

## Мультимовність (Flask‑Babel)

- Підтримувані локалі: uk, de, en
- Визначення мови: спочатку `session['language']`, інакше best‑match з заголовків браузера
- Файл `app/babel.py` керує ініціалізацією та вибором локалі.

---

## Розгортання (Render / Gunicorn)

- Налаштуйте змінні оточення в Render: `SECRET_KEY`, `DATABASE_URL`, `DB_SCHEMA` (за потреби), `BASE_URL`, поштові змінні
- Команда запуску для Gunicorn з Socket.IO:
  - `gunicorn --worker-class eventlet -w 1 run:app`
- Застосовуйте міграції при деплої: `flask db upgrade`

---

## Типові проблеми та рішення

- ModuleNotFoundError (наприклад, `flask_wtf`):
  - Перевірте встановлення: `py -m pip install -r requirements.txt`
- OSError [WinError 10048] (порт зайнятий):
  - Задайте інший порт: `$env:PORT="8081"; py run.py`
- `no such table: ...` (SQLite):
  - Застосуйте міграції: `$env:FLASK_APP="run.py"; flask db upgrade`
  - Переконайтесь у правильності `DATABASE_URL` чи наявності `site.db`
- Попередження про PATH у Windows (скрипти в `...\Python\Scripts` не в PATH):
  - Це не критично; за потреби додайте шлях до змінної PATH користувача.

---

## Внесок і розробка

- Pull‑request’и вітаються. Переконайтесь, що локальні БД/кеш не потрапляють у git.
- `.gitignore` вже виключає `site.db` та `instance/`.

---

## Ліцензія

TBD (буде додано).
