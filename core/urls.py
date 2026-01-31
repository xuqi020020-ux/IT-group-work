from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("documents/new/", views.document_create, name="document_create"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
    path("documents/<int:pk>/edit/", views.document_edit, name="document_edit"),
    path("documents/<int:pk>/delete/", views.document_delete, name="document_delete"),
    path("documents/<int:pk>/share/", views.document_share, name="document_share"),

]

