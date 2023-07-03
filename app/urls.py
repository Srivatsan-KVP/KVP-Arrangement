from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('master/', views.master),
    path('upload/', views.upload),
    path('arrangement/', views.arrangement),
    path('saved/', views.saved),
    path('logout/', views.logout),
]
