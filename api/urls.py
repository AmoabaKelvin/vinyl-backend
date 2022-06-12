from django.urls import path

from . import views

urlpatterns = [
    path('songs/', views.SongList.as_view()),
    path('songs/<int:id>', views.SongDetail.as_view()),
    path('users/<int:id>', views.UserDetailView.as_view()),
]
