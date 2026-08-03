from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dm/nouvelle/", views.demande_creer, name="demande_creer"),
    path("dm/<int:pk>/", views.demande_detail, name="demande_detail"),
    path("dm/<int:pk>/modifier/", views.demande_modifier, name="demande_modifier"),
    path("dm/<int:pk>/supprimer/", views.demande_supprimer, name="demande_supprimer"),
]
