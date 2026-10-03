from .models import SiteInfo


def site_info(request):
    """Expose the SiteInfo singleton to every template (footer links, CTA)."""
    return {"site_info": SiteInfo.load()}
