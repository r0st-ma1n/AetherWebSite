from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()


@register.simple_tag
def field(obj, base_name):
    """Return obj.<base_name>_ru or obj.<base_name>_en depending on the active language.

    The site content is entered by a single trusted admin, so the value is
    returned marked safe to allow basic HTML in doc/feature text.
    """
    suffix = "en" if get_language() == "en" else "ru"
    value = getattr(obj, f"{base_name}_{suffix}", "")
    return mark_safe(value)
