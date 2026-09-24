from django.core.management.base import BaseCommand

from website.models import DocPage, Feature, SiteInfo

FEATURES = [
    {
        "icon": "🖱️",
        "title_ru": "Drag-and-drop дизайнер интерфейса",
        "title_en": "Drag-and-drop UI designer",
        "description_ru": "Собирайте интерфейс плагина из готовых компонентов — Knob, Slider, Button — прямо на canvas, без единой строки кода.",
        "description_en": "Build your plugin's interface from ready-made components — knobs, sliders, buttons — directly on the canvas, without writing a line of code.",
        "order": 1,
    },
    {
        "icon": "🔄",
        "title_ru": "Двусторонняя синхронизация с кодом",
        "title_en": "Two-way code synchronization",
        "description_ru": "Изменения в визуальном дизайнере сразу превращаются в синхронизированный C++ код — и наоборот.",
        "description_en": "Changes in the visual designer are instantly reflected in synchronized C++ code — and the other way around.",
        "order": 2,
    },
    {
        "icon": "🧩",
        "title_ru": "Группировка, выравнивание, undo/redo",
        "title_en": "Grouping, alignment, undo/redo",
        "description_ru": "Выделяйте несколько компонентов рамкой, выравнивайте и распределяйте их группой. История изменений — до 100 шагов отмены.",
        "description_en": "Select multiple components with a marquee, align and distribute them as a group. Full undo/redo history with up to 100 steps.",
        "order": 3,
    },
    {
        "icon": "💻",
        "title_ru": "Встроенный редактор Monaco",
        "title_en": "Built-in Monaco editor",
        "description_ru": "Редактируйте C++ код прямо в IDE — с подсветкой синтаксиса, файловым проводником и live-обновлением.",
        "description_en": "Edit C++ code right inside the IDE — with syntax highlighting, a file explorer, and live updates.",
        "order": 4,
    },
    {
        "icon": "🎚️",
        "title_ru": "Собственный C++ фреймворк для аудио",
        "title_en": "A native C++ audio framework",
        "description_ru": "Aether Framework берёт на себя низкоуровневую обработку звука, чтобы вы сосредоточились на дизайне и логике плагина.",
        "description_en": "The Aether framework handles low-level audio processing, so you can focus on the plugin's design and logic.",
        "order": 5,
    },
    {
        "icon": "✅",
        "title_ru": "Валидация проектов",
        "title_en": "Project validation",
        "description_ru": "Файлы проекта .aether проверяются по JSON Schema — ошибки конфигурации видны сразу, а не во время сборки.",
        "description_en": "Project .aether files are validated against a JSON Schema — configuration errors surface immediately, not at build time.",
        "order": 6,
    },
]

DOCS = [
    {
        "slug": "getting-started",
        "title_ru": "Начало работы",
        "title_en": "Getting started",
        "content_ru": (
            "<p>AetherIDE — это desktop-приложение для визуальной разработки аудио-плагинов. "
            "Вы собираете интерфейс плагина из компонентов на canvas, а IDE автоматически "
            "поддерживает синхронизированный C++ код на основе фреймворка Aether.</p>"
            "<p>Типичный рабочий процесс: создать проект, разместить компоненты интерфейса "
            "(регуляторы, слайдеры, кнопки), связать их с параметрами звука, при необходимости "
            "донастроить логику во встроенном редакторе кода — и собрать готовый плагин.</p>"
        ),
        "content_en": (
            "<p>AetherIDE is a desktop application for visually building audio plugins. "
            "You assemble the plugin's interface from components on a canvas, while the IDE "
            "automatically keeps synchronized C++ code based on the Aether framework.</p>"
            "<p>A typical workflow: create a project, place UI components (knobs, sliders, "
            "buttons), bind them to audio parameters, fine-tune the logic in the built-in code "
            "editor if needed, and build the finished plugin.</p>"
        ),
        "order": 1,
    },
]


class Command(BaseCommand):
    help = "Seed the database with initial AetherIDE content (features, docs, site info)."

    def handle(self, *args, **options):
        for data in FEATURES:
            obj, created = Feature.objects.update_or_create(
                title_ru=data["title_ru"], defaults=data
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} feature: {obj}")

        for data in DOCS:
            obj, created = DocPage.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} doc page: {obj}")

        site_info = SiteInfo.load()
        if not site_info.about_ru and not site_info.about_en:
            site_info.about_ru = (
                "AetherIDE — визуальная IDE для разработки аудио-плагинов. "
                "Проект развивается независимым автором."
            )
            site_info.about_en = (
                "AetherIDE is a visual IDE for building audio plugins, "
                "developed by an independent author."
            )
            site_info.save()
            self.stdout.write("Filled in default site info.")

        self.stdout.write(self.style.SUCCESS("Content seeding complete."))
