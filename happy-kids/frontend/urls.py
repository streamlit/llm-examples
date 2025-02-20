from django.urls import path
from . import views
from django.urls import path

urlpatterns = [
    path('', views.view_home, name='home'),
    path('lulu', views.view_lulu, name='lulu'),
    path('adm/users_page', views.view_users, name='users_page'),
    path('adm/trainingFiles', views.training_list, name='training_list'),
    path('profile', views.view_profile, name='profile'),
    path('memory', views.view_chat_memory, name='chat_memory'),
    path('adm/adm_onboarding_questions', views.view_chat_management_onboarding_questions, name='adm_onboarding_questions')
]