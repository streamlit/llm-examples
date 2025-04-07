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
    path('memos', views.view_chat_memos, name='chat_memos'),
    path('emotions_atlas', views.view_emotions_atlas, name='emotions_atlas'),
    path('ideas_box', views.view_ideas_box, name='ideas_box'),
    path('diary', views.view_diary, name='diary'),
    path('surprise_me', views.view_surprise_me, name='suprise_me'),

    path('adm/adm_onboarding_questions', views.view_chat_management_onboarding_questions, name='adm_onboarding_questions'),
    path('update-question-active/<int:id>/', views.update_question_active, name='update_question_active'),
    path('add_option/', views.add_option, name="add_option"),
    path('delete_option/<int:option_id>/', views.delete_option, name="delete_option"),
    path('onboarding-data/', views.onboarding_data, name='onboarding-data'),
    path('save-onboarding-answer/', views.save_onboarding_answer, name='save_onboarding_answer'),   
    path('check-onboarding-completed/', views.check_onboarding_completed, name='check_onboarding_completed'),
    path('save_memos/', views.view_save_memo, name='save_memos'),
    path('delete_memo/<int:memo_id>/', views.view_delete_memo, name="delete_memo"),
    path("save_feedback/", views.view_save_feedback, name="save_feedback"),
    
    path('adm/adm_am_i_boring_questions', views.view_management_am_i_boring_questions, name='adm_am_i_boring_questions'),
    path('add_option_am_i_boring/', views.add_option_am_i_boring, name="add_option_am_i_boring"),
    path('delete_option_am_i_boring/<int:option_id>/', views.delete_option_am_i_boring, name="delete_option_am_i_boring"),
    path('am-i-boring-data/', views.am_i_boring_data, name='am_i_boring_data'),
    path('update-question-active-am-i-boring/<int:id>/', views.update_question_active_am_i_boring, name='update_question_active'),
    path('save-am-i-boring-answer/', views.save_am_i_boring_answer, name='save_am_i_boring_answer'),  

    path('create_diary/', views.create_diary, name='create_diary'),
    path("generate_suggestions/", views.generate_suggestions, name="generate_suggestions"),

]