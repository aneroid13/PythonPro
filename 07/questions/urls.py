from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.lv.as_view(), name="index"),
    path('question/', views.question.as_view(), name="question"),
    path('login/', views.login),
    path('ask/', views.ask),
    path('search/', views.search),
    path('signup/', views.signup),
    path('tags/', views.tags)
]