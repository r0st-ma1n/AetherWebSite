# AetherWebSite

Сайт-визитка **AetherIDE** — визуальной IDE для аудио-плагинов. Django 6.1, PostgreSQL, Tailwind CSS, два языка (RU/EN). Весь контент — фичи, скриншоты, документация, контакты — редактируется через админку.

**Стек:** Python 3.13+ · Django 6.1 · PostgreSQL 16 · Tailwind CSS 3 (сборка через Node.js) · gunicorn + nginx + certbot в продакшене.

## Локальный запуск

Нужны Python 3.13+, Node.js 20+ и Docker (для Postgres).

```powershell
# 1. Окружение
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env            # значения по умолчанию подходят для локальной разработки

# 2. База данных (PostgreSQL в Docker, порт 5432)
docker compose up -d db
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py seed_content      # стартовый контент, один раз
venv\Scripts\python manage.py createsuperuser   # доступ в /admin/

# 3. Стили
npm install
npm run build:css

# 4. Сервер
venv\Scripts\python manage.py runserver
```

| Адрес | Что там |
|---|---|
| http://127.0.0.1:8000/ | сайт на русском (язык по умолчанию, без префикса) |
| http://127.0.0.1:8000/en/ | английская версия |
| http://127.0.0.1:8000/admin/ | админка |

Логин и пароль админа нигде в репозитории не хранятся — создайте их сами через `createsuperuser`.

### Стили (Tailwind)

`static/css/site.css` генерируется из шаблонов и не коммитится. Исходники — `frontend/site.css` и `frontend/tailwind.config.js`.

```powershell
npm run build:css    # разовая сборка (минифицированная)
npm run watch:css    # пересборка при изменении шаблонов — держите открытой во время вёрстки
```

Если на странице нет стилей — скорее всего, CSS не собран. В Docker-образе он собирается автоматически.

### Без Docker

Для быстрого просмотра можно обойтись без Postgres — укажите SQLite в `.env`:

```ini
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

## Переменные окружения

Все настройки читаются из `.env` (шаблон — `.env.example`). Сам `.env` не коммитится.

| Переменная | Назначение |
|---|---|
| `SECRET_KEY` | секретный ключ Django; для продакшена сгенерируйте новый (команда есть в `.env.example`) |
| `DEBUG` | `True` локально, `False` в продакшене |
| `ALLOWED_HOSTS` | домены через запятую, например `aetheride.ru,www.aetheride.ru` |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | подключение к БД; по умолчанию Postgres на `localhost:5432` |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | почта; по умолчанию письма печатаются в консоль |

`docker compose` тоже читает `.env` и подставляет `$VAR`, поэтому буквальный `$` в значениях экранируйте как `$$`.

## Тесты

```powershell
venv\Scripts\python manage.py test
```

Тесты используют БД из `.env` (Postgres должен быть поднят). Прогнать без Postgres, на SQLite в памяти:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
venv\Scripts\python manage.py test
```

## Продакшен (Docker)

`docker-compose.prod.yml` поднимает четыре сервиса: `db` (Postgres), `web` (Django + gunicorn), `nginx` (раздаёт статику и медиа, проксирует на `web`) и `certbot` (сертификаты Let's Encrypt).

```bash
# на сервере, в .env: DEBUG=False, свой SECRET_KEY, ALLOWED_HOSTS, пароль БД
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py seed_content
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

При старте контейнер `web` сам выполняет `migrate` и `collectstatic` (см. `entrypoint.sh`). Tailwind собирается на отдельной стадии Dockerfile.

**Автодеплой.** Каждый push в `master` запускает `.github/workflows/deploy.yml`: тесты → сборка образа и публикация в `ghcr.io/r0st-ma1n/aetherwebsite` (теги `latest` и SHA коммита) → по SSH на сервере `pull` + `up -d`. Нужны секреты репозитория: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH` (папка с `.env` и `nginx/` на сервере), `DEPLOY_SSH_KEY` (приватный ключ, публичный — в `~/.ssh/authorized_keys` на сервере). `docker-compose.prod.yml` при деплое перезаписывается версией из репозитория.

Откат на прошлый коммит (на сервере):

```bash
IMAGE_TAG=<sha> docker compose -f docker-compose.prod.yml up -d --no-build web
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

**HTTPS.** Сначала работает только `nginx/conf.d/app-http.conf` (порт 80 и ACME-challenge). После выпуска сертификата:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d aetheride.ru -d www.aetheride.ru
mv nginx/conf.d/app-http.conf nginx/conf.d/app-http.conf.disabled
mv nginx/conf.d/app-ssl.conf.disabled nginx/conf.d/app-ssl.conf
docker compose -f docker-compose.prod.yml restart nginx
```

## Структура проекта

```
aether_site/          настройки Django, корневые URL (i18n_patterns, RU без префикса)
website/
  models.py           Feature, Screenshot, DocPage, SiteInfo (синглтон), ContactMessage
  views.py, urls.py   страницы сайта
  forms.py            форма обратной связи
  context_processors.py  SiteInfo доступен во всех шаблонах
  templatetags/       теги field/field_text (RU/EN-поле по языку) и icon (SVG-иконки)
  management/commands/seed_content.py  стартовые фичи и документация
templates/website/    шаблоны страниц; файлы с «_» — переиспользуемые фрагменты
frontend/             исходники Tailwind (site.css, tailwind.config.js)
static/               статика: js/site.js, img/, css/site.css (генерируется)
locale/en/            английский перевод строк интерфейса
nginx/conf.d/         конфиги nginx для продакшена
```

## Разделы сайта

- **Главная** — hero, ключевые возможности, призыв к действию
- **Возможности** (`/features/`) — список фич из админки
- **Скриншоты** (`/gallery/`) — галерея с лайтбоксом, картинки загружаются в админке
- **Документация** (`/docs/`, `/docs/<slug>/`) — страницы с HTML-контентом
- **Контакты** (`/contacts/`) — форма обратной связи; сообщения сохраняются в админке

## Контент и переводы

У каждой модели есть пары полей `*_ru` / `*_en` — шаблон берёт нужное по текущему языку. Флаг «Опубликовано» скрывает запись с сайта, поле «Порядок» задаёт сортировку.

Статические строки интерфейса (меню, кнопки) переводятся через gettext. После правки шаблонов:

```powershell
venv\Scripts\python manage.py makemessages -l en
# отредактируйте locale/en/LC_MESSAGES/django.po
venv\Scripts\python manage.py compilemessages
```
