# AetherWebSite

Сайт-визитка AetherIDE на Django (RU/EN), контент редактируется через админку.

## Запуск

```powershell
venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env   # заполните под своё окружение
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py seed_content   # наполнить стартовым контентом (один раз)
venv\Scripts\python manage.py runserver
```

Сайт: http://127.0.0.1:8000/ (RU) и http://127.0.0.1:8000/en/ (EN)
Админку создайте локально командой `manage.py createsuperuser` — логин и пароль нигде не хранятся в репозитории.

### Переменные окружения (`.env`)

`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, настройки БД (`DB_*`) и почты (`EMAIL_*`) читаются из `.env` (см. `.env.example`). Файл `.env` не коммитится.

### Тесты

```powershell
venv\Scripts\python manage.py test
```

По умолчанию тесты используют ту же БД, что указана в `.env` (Postgres). Чтобы прогнать их без поднятого Postgres — на sqlite в памяти:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
venv\Scripts\python manage.py test
```

## Структура

- `website/` — приложение: модели `Feature`, `Screenshot`, `DocPage`, `SiteInfo`, `ContactMessage`, всё редактируется в `/admin/`
- `templates/website/` — шаблоны (Tailwind CSS через CDN)
- `locale/en/` — английский перевод статических строк интерфейса (заголовки меню, кнопки)
- `website/management/commands/seed_content.py` — сидинг стартовых фич/документации

## Разделы сайта

Главная, Возможности, Скриншоты (загружаются в админке), Документация, Контакты (с формой обратной связи, сообщения сохраняются в админке).
