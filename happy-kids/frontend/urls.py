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
    


    path('adm/adm_onboarding_questions', views.view_chat_management_onboarding_questions, name='adm_onboarding_questions'),

    path('update-question-active/<int:id>/', views.update_question_active, name='update_question_active'),
    path('add_option/', views.add_option, name="add_option"),
    path('delete_option/<int:option_id>/', views.delete_option, name="delete_option"),

    path('onboarding-data/', views.onboarding_data, name='onboarding-data'),
    path('save-onboarding-answer/', views.save_onboarding_answer, name='save_onboarding_answer'),   
    path('check-onboarding-completed/', views.check_onboarding_completed, name='check_onboarding_completed'),

    path('diary', views.view_diary, name='diary'),
    path('create_diary/', views.create_diary, name='create_diary'),

]