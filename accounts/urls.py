from django.urls import path

from . import views

urlpatterns = [
    path('register', views.SignUpView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.CustomLogoutView.as_view(), name='logout'),
    path('delete', views.delete_user_account, name='delete'),
]
