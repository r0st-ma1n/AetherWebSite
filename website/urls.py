from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("features/", views.features, name="features"),
    path("gallery/", views.gallery, name="gallery"),
    path("docs/", views.docs_list, name="docs_list"),
    path("docs/<slug:slug>/", views.doc_detail, name="doc_detail"),
    path("contacts/", views.contacts, name="contacts"),
]
