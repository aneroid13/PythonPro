from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('question/<int:pk>', views.QuestionView.as_view(), name="question"),
    path('login/', views.LoginUser.as_view(), name="login"),
    path('logout/', views.LogoutUser.as_view(), name="logout"),
    path('ask/', views.AskView.as_view(), name="ask"),
    path('search/', views.SearchView.as_view(), name="search"),
    path('signup/', views.SignUpUser.as_view(), name="signup"),
    path('tags/', views.tags, name="tags"),
    path('settings/<slug:username>', views.UserSettingsView.as_view(), name="user")
]
