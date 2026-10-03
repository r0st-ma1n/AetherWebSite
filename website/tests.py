from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .forms import ContactForm
from .models import ContactMessage, DocPage, Feature, Screenshot, SiteInfo


class FeatureModelTests(TestCase):
    def setUp(self):
        self.feature = Feature.objects.create(
            title_ru="Заголовок", title_en="Title",
            description_ru="Описание", description_en="Description",
        )

    def test_title_and_description_pick_language(self):
        self.assertEqual(self.feature.title("ru"), "Заголовок")
        self.assertEqual(self.feature.title("en"), "Title")
        self.assertEqual(self.feature.description("ru"), "Описание")
        self.assertEqual(self.feature.description("en"), "Description")

    def test_unknown_language_falls_back_to_russian(self):
        self.assertEqual(self.feature.title("fr"), "Заголовок")

    def test_str_returns_russian_title(self):
        self.assertEqual(str(self.feature), "Заголовок")

    def test_default_ordering(self):
        Feature.objects.all().delete()
        first = Feature.objects.create(title_ru="A", title_en="A", order=2)
        second = Feature.objects.create(title_ru="B", title_en="B", order=1)
        self.assertEqual(list(Feature.objects.all()), [second, first])


class ScreenshotModelTests(TestCase):
    def test_caption_picks_language_and_defaults_to_empty(self):
        shot = Screenshot.objects.create(image="screenshots/test.png", caption_ru="Подпись")
        self.assertEqual(shot.caption("ru"), "Подпись")
        self.assertEqual(shot.caption("en"), "")

    def test_str_falls_back_to_image_name_without_caption(self):
        shot = Screenshot.objects.create(image="screenshots/test.png")
        self.assertEqual(str(shot), shot.image.name)


class DocPageModelTests(TestCase):
    def test_title_and_content_pick_language(self):
        doc = DocPage.objects.create(
            slug="getting-started",
            title_ru="Начало", title_en="Getting started",
            content_ru="<p>Рус</p>", content_en="<p>En</p>",
        )
        self.assertEqual(doc.title("en"), "Getting started")
        self.assertEqual(doc.content("ru"), "<p>Рус</p>")


class SiteInfoModelTests(TestCase):
    def test_load_creates_singleton(self):
        self.assertEqual(SiteInfo.objects.count(), 0)
        info = SiteInfo.load()
        self.assertEqual(SiteInfo.objects.count(), 1)
        self.assertEqual(SiteInfo.load().pk, info.pk)

    def test_about_picks_language(self):
        info = SiteInfo.load()
        info.about_ru = "О нас"
        info.about_en = "About us"
        info.save()
        self.assertEqual(info.about("ru"), "О нас")
        self.assertEqual(info.about("en"), "About us")


class ContactMessageModelTests(TestCase):
    def test_str_includes_name_and_email(self):
        message = ContactMessage.objects.create(
            name="Ada", email="ada@example.com", message="Hi"
        )
        self.assertEqual(str(message), "Ada <ada@example.com>")


class ContactFormTests(TestCase):
    def test_valid_data(self):
        form = ContactForm(data={
            "name": "Ada",
            "email": "ada@example.com",
            "message": "Hello there",
        })
        self.assertTrue(form.is_valid())

    def test_missing_required_fields_invalid(self):
        form = ContactForm(data={"name": "", "email": "", "message": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("message", form.errors)

    def test_invalid_email_rejected(self):
        form = ContactForm(data={
            "name": "Ada", "email": "not-an-email", "message": "Hello",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class HomeViewTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_only_shows_published_features(self):
        Feature.objects.create(title_ru="Видна", title_en="Visible", is_published=True)
        Feature.objects.create(title_ru="Скрыта", title_en="Hidden", is_published=False)
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "Видна")
        self.assertNotContains(response, "Скрыта")

    def test_home_page_limits_features_to_four(self):
        for i in range(6):
            Feature.objects.create(title_ru=f"F{i}", title_en=f"F{i}", order=i)
        response = self.client.get(reverse("website:home"))
        self.assertEqual(len(response.context["features"]), 4)


class FeaturesViewTests(TestCase):
    def test_lists_only_published_features(self):
        Feature.objects.create(title_ru="Видна", title_en="Visible", is_published=True)
        Feature.objects.create(title_ru="Скрыта", title_en="Hidden", is_published=False)
        response = self.client.get(reverse("website:features"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Видна")
        self.assertNotContains(response, "Скрыта")


class GalleryViewTests(TestCase):
    def test_lists_only_published_screenshots(self):
        Screenshot.objects.create(image="screenshots/a.png", caption_ru="Видна", is_published=True)
        Screenshot.objects.create(image="screenshots/b.png", caption_ru="Скрыта", is_published=False)
        response = self.client.get(reverse("website:gallery"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Видна")
        self.assertNotContains(response, "Скрыта")


class DocsListViewTests(TestCase):
    def test_lists_only_published_docs(self):
        DocPage.objects.create(
            slug="visible", title_ru="Видна", title_en="Visible",
            content_ru="x", content_en="x", is_published=True,
        )
        DocPage.objects.create(
            slug="hidden", title_ru="Скрыта", title_en="Hidden",
            content_ru="x", content_en="x", is_published=False,
        )
        response = self.client.get(reverse("website:docs_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Видна")
        self.assertNotContains(response, "Скрыта")


class DocDetailViewTests(TestCase):
    def test_published_doc_is_visible(self):
        doc = DocPage.objects.create(
            slug="getting-started", title_ru="Начало", title_en="Getting started",
            content_ru="<p>Текст</p>", content_en="<p>Text</p>", is_published=True,
        )
        response = self.client.get(reverse("website:doc_detail", args=[doc.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Начало")

    def test_unpublished_doc_returns_404(self):
        doc = DocPage.objects.create(
            slug="draft", title_ru="Черновик", title_en="Draft",
            content_ru="x", content_en="x", is_published=False,
        )
        response = self.client.get(reverse("website:doc_detail", args=[doc.slug]))
        self.assertEqual(response.status_code, 404)

    def test_missing_doc_returns_404(self):
        response = self.client.get(reverse("website:doc_detail", args=["does-not-exist"]))
        self.assertEqual(response.status_code, 404)


class ContactsViewTests(TestCase):
    def test_get_renders_empty_form(self):
        response = self.client.get(reverse("website:contacts"))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_message_and_redirects(self):
        response = self.client.post(reverse("website:contacts"), {
            "name": "Ada",
            "email": "ada@example.com",
            "message": "Hello there",
        })
        self.assertRedirects(response, reverse("website:contacts"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.name, "Ada")
        self.assertEqual(saved.email, "ada@example.com")

    def test_invalid_post_does_not_create_message(self):
        response = self.client.post(reverse("website:contacts"), {
            "name": "", "email": "not-an-email", "message": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_english_form_labels_are_translated(self):
        with translation.override("en"):
            response = self.client.get("/en/contacts/")
        self.assertContains(response, ">Name<")
        self.assertContains(response, ">Message<")
        self.assertNotContains(response, ">Имя<")
        self.assertNotContains(response, ">Сообщение<")


class LanguageSwitchTests(TestCase):
    def test_default_locale_is_russian(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "Возможности")

    def test_english_prefix_switches_locale(self):
        with translation.override("en"):
            response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Features")


class FieldTemplateTagTests(TestCase):
    def render(self, source, **context):
        from django.template import Context, Template
        return Template("{% load website_extras %}" + source).render(Context(context))

    def test_field_keeps_html(self):
        doc = DocPage(title_ru="<b>Начало</b>")
        self.assertEqual(self.render('{% field doc "title" %}', doc=doc), "<b>Начало</b>")

    def test_field_text_is_safe_inside_attributes(self):
        shot = Screenshot(caption_ru='Окно "Дизайнер" & <i>код</i>')
        html = self.render("""<img alt="{% field_text shot 'caption' %}">""", shot=shot)
        self.assertEqual(html, '<img alt="Окно &quot;Дизайнер&quot; &amp; код">')

    def test_field_text_decodes_entities_before_escaping(self):
        shot = Screenshot(caption_ru="A &amp; B")
        self.assertEqual(self.render("{% field_text shot 'caption' %}", shot=shot), "A &amp; B")


class IconTemplateTagTests(TestCase):
    def render(self, source, **context):
        from django.template import Context, Template
        return Template("{% load website_extras %}" + source).render(Context(context))

    def test_known_icon_renders_svg(self):
        html = self.render('{% icon "code" "w-5 h-5" %}')
        self.assertTrue(html.startswith('<svg class="w-5 h-5"'))

    def test_unknown_icon_falls_back_to_escaped_text(self):
        html = self.render("{% icon name %}", name="🎛️<b>")
        self.assertIn("🎛️&lt;b&gt;", html)
        self.assertNotIn("<svg", html)

    def test_seeded_features_use_svg_icons(self):
        from .management.commands.seed_content import FEATURES
        from .templatetags.website_extras import ICONS
        for data in FEATURES:
            self.assertIn(data["icon"], ICONS, data["title_en"])


class LayoutTests(TestCase):
    def test_uses_built_stylesheet_instead_of_tailwind_cdn(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "css/site.css")
        self.assertNotContains(response, "cdn.tailwindcss.com")

    def test_mobile_menu_has_navigation_links(self):
        html = self.client.get(reverse("website:home")).content.decode()
        mobile_menu = html[html.index("<details"):html.index("</details>")]
        self.assertIn('href="%s"' % reverse("website:contacts"), mobile_menu)

    def test_footer_links_to_github_when_set(self):
        SiteInfo.objects.update_or_create(pk=1, defaults={"github_url": "https://github.com/example/aether"})
        response = self.client.get(reverse("website:features"))
        self.assertContains(response, 'href="https://github.com/example/aether"')

    def test_home_has_interactive_designer_demo(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'role="slider"', count=3)
        self.assertContains(response, 'id="code-threshold"')

    def test_mobile_menu_label_is_translated(self):
        self.assertContains(self.client.get("/"), ">Меню<")
        with translation.override("en"):
            self.assertContains(self.client.get("/en/"), ">Menu<")

    def test_html_lang_matches_active_language(self):
        self.assertContains(self.client.get("/"), '<html lang="ru"')
        with translation.override("en"):
            self.assertContains(self.client.get("/en/"), '<html lang="en"')
