from html import unescape

from django import template
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()


def _localized(obj, base_name):
    suffix = "en" if get_language() == "en" else "ru"
    return getattr(obj, f"{base_name}_{suffix}", "") or ""


@register.simple_tag
def field(obj, base_name):
    """Return obj.<base_name>_ru or obj.<base_name>_en depending on the active language.

    The site content is entered by a single trusted admin, so the value is
    returned marked safe to allow basic HTML in doc/feature text.
    """
    return mark_safe(_localized(obj, base_name))


@register.simple_tag
def field_text(obj, base_name):
    """Like ``field``, but as plain text for attributes and <title>.

    HTML tags and entities are removed and the result is left unsafe, so
    autoescaping handles quotes and ampersands exactly once.
    """
    return unescape(strip_tags(_localized(obj, base_name)))


# Stroke icons on a 24x24 grid. Feature.icon holds one of these names; anything
# else (e.g. an emoji entered before icons existed) is rendered as plain text.
ICONS = {
    "knob": '<circle cx="12" cy="12" r="8"/><path d="M12 12 7.5 7.5"/><path d="M12 2v1.5M22 12h-1.5M2 12h1.5"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "sync": '<path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/>',
    "wave": '<path d="M2 12h3l2-6 3 12 3-9 2 6 2-3h5"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5M2 17l10 5 10-5"/>',
    "cursor": '<path d="m4 4 7 17 2.5-7.5L21 11z"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "editor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "package": '<path d="m12 2 9 5v10l-9 5-9-5V7z"/><path d="m3 7 9 5 9-5M12 12v10"/>',
    "plug": '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.5 2.5L16 9.5"/>',
}


@register.simple_tag
def icon(name, css_class="w-6 h-6"):
    """Inline SVG for a known icon name; unknown values fall back to escaped text."""
    paths = ICONS.get((name or "").strip())
    if paths is None:
        return format_html('<span class="text-2xl leading-none" aria-hidden="true">{}</span>', name or "")
    return format_html(
        '<svg class="{}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>',
        css_class,
        mark_safe(paths),
    )
