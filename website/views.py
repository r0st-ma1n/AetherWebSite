from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import get_language, gettext as _

from .forms import ContactForm
from .models import DocPage, Feature, Screenshot, SiteInfo


def home(request):
    lang = get_language()
    features = Feature.objects.filter(is_published=True)
    screenshots = Screenshot.objects.filter(is_published=True)[:3]
    return render(
        request,
        "website/home.html",
        {"features": features, "screenshots": screenshots, "lang": lang},
    )


def features(request):
    lang = get_language()
    return render(
        request,
        "website/features.html",
        {"features": Feature.objects.filter(is_published=True), "lang": lang},
    )


def gallery(request):
    lang = get_language()
    return render(
        request,
        "website/gallery.html",
        {"screenshots": Screenshot.objects.filter(is_published=True), "lang": lang},
    )


def docs_list(request):
    lang = get_language()
    return render(
        request,
        "website/docs_list.html",
        {"docs": DocPage.objects.filter(is_published=True), "lang": lang},
    )


def doc_detail(request, slug):
    lang = get_language()
    doc = get_object_or_404(DocPage, slug=slug, is_published=True)
    return render(request, "website/doc_detail.html", {"doc": doc, "lang": lang})


def contacts(request):
    lang = get_language()
    site_info = SiteInfo.load()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Сообщение отправлено. Спасибо!"))
            return redirect("website:contacts")
    else:
        form = ContactForm()
    return render(
        request,
        "website/contacts.html",
        {"form": form, "site_info": site_info, "lang": lang},
    )
