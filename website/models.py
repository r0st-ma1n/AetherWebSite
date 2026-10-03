from django.db import models


class Feature(models.Model):
    """A single IDE capability shown on the home/features pages."""

    icon = models.CharField(
        max_length=10,
        blank=True,
        help_text="Icon name: knob, sliders, code, sync, wave, layers, cursor, cpu, editor, package, plug, check. Any other text (e.g. an emoji) is shown as is.",
    )
    title_ru = models.CharField("Заголовок (RU)", max_length=200)
    title_en = models.CharField("Title (EN)", max_length=200)
    description_ru = models.TextField("Описание (RU)")
    description_en = models.TextField("Description (EN)")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Возможность"
        verbose_name_plural = "Возможности"

    def __str__(self):
        return self.title_ru

    def title(self, language_code):
        return self.title_en if language_code == "en" else self.title_ru

    def description(self, language_code):
        return self.description_en if language_code == "en" else self.description_ru


class Screenshot(models.Model):
    """A screenshot of the IDE shown in the gallery."""

    image = models.ImageField("Изображение", upload_to="screenshots/")
    caption_ru = models.CharField("Подпись (RU)", max_length=200, blank=True)
    caption_en = models.CharField("Caption (EN)", max_length=200, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Скриншот"
        verbose_name_plural = "Скриншоты"

    def __str__(self):
        return self.caption_ru or self.image.name

    def caption(self, language_code):
        return (self.caption_en if language_code == "en" else self.caption_ru) or ""


class DocPage(models.Model):
    """A documentation article, identified by a slug shared across languages."""

    slug = models.SlugField("Слаг", unique=True)
    title_ru = models.CharField("Заголовок (RU)", max_length=200)
    title_en = models.CharField("Title (EN)", max_length=200)
    content_ru = models.TextField("Содержимое (RU)", help_text="Поддерживается базовый HTML.")
    content_en = models.TextField("Content (EN)", help_text="Basic HTML is supported.")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Страница документации"
        verbose_name_plural = "Документация"

    def __str__(self):
        return self.title_ru

    def title(self, language_code):
        return self.title_en if language_code == "en" else self.title_ru

    def content(self, language_code):
        return self.content_en if language_code == "en" else self.content_ru


class SiteInfo(models.Model):
    """Singleton-style block with about/contact information, editable in the admin."""

    about_ru = models.TextField("О проекте (RU)", blank=True)
    about_en = models.TextField("About (EN)", blank=True)
    contact_email = models.EmailField("Email для связи", blank=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Информация о проекте"
        verbose_name_plural = "Информация о проекте"

    def __str__(self):
        return "Информация о проекте"

    def about(self, language_code):
        return self.about_en if language_code == "en" else self.about_ru

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    """A message submitted through the contact form."""

    name = models.CharField("Имя", max_length=200)
    email = models.EmailField("Email")
    message = models.TextField("Сообщение")
    created_at = models.DateTimeField("Отправлено", auto_now_add=True)
    is_read = models.BooleanField("Прочитано", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сообщение с формы обратной связи"
        verbose_name_plural = "Сообщения с формы обратной связи"

    def __str__(self):
        return f"{self.name} <{self.email}>"
