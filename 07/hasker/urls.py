"""
URL configuration for hasker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('questions.urls', namespace="qu")),
    # path('question/', q_views.question),
    # path('login/', q_views.login),
    # path('ask/', q_views.ask),
    # path('search/', q_views.search),
    # path('signup/', q_views.signup),
    # path('tags/', q_views.tags),
    path('admin/', admin.site.urls)
]
