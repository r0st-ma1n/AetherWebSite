from django.contrib import admin

from .models import ContactMessage, DocPage, Feature, Screenshot, SiteInfo


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "title_en", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title_ru", "title_en")


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(DocPage)
class DocPageAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "title_en", "slug", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title_en",)}
    search_fields = ("title_ru", "title_en", "slug")


@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "contact_email", "updated_at")

    def has_add_permission(self, request):
        return not SiteInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_editable = ("is_read",)
    list_filter = ("is_read",)
    readonly_fields = ("name", "email", "message", "created_at")
    search_fields = ("name", "email", "message")
