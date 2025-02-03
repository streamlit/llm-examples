from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_home, name='home'),
    path('lulu', views.view_lulu, name='lulu'),
    path('users_page', views.view_users, name='users_page'),
    path('trainingFiles', views.training_list, name='training_list'),
    path('profile', views.view_profile, name='profile')
]